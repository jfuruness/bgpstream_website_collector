import csv
from datetime import date
from pathlib import Path
from typing import Any, Optional

import bs4
from requests.adapters import HTTPAdapter, Retry
import requests_cache
from tqdm import tqdm

# Since this is type ignored, mypy doesn't see the import
from .front_page_info import FrontPageInfo  # type: ignore
from .rows import Row
from .utils import get_tags


class BGPStreamWebsiteCollector:
    """This class parses bgpstream.com information"""

    URL = "https://bgpstream.com"

    def __init__(
        self,
        csv_path: Path = Path.home() / "Desktop" / "bgpstream_website.csv",
        requests_cache_db_path: Optional[Path] = None,
    ) -> None:
        self.csv_path: Path = csv_path

        # By default keep requests cached for a single day
        if requests_cache_db_path is None:
            requests_cache_db_path = Path("/tmp/") / f"{date.today()}.db"
        self.requests_cache_db_path: Path = requests_cache_db_path
        self.session = requests_cache.CachedSession(str(self.requests_cache_db_path))

        # https://stackoverflow.com/a/35636367
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def __del__(self):
        self.session.close()

    def run(self) -> list[dict[str, Any]]:
        """Inserts info from bgpstream.com into a csv"""

        csv_rows = []
        # Parses rows if they are the event types desired
        rows: list[Row] = self._get_rows()
        for row in tqdm(rows, desc="Parsing BGPStream.com", total=len(rows)):
            # Parses the row into csv format. Can't do with mp, rate limited
            csv_rows.append(row.parse(self.session))
        self._write_csv(csv_rows)
        return csv_rows

    def _get_rows(self) -> list[Row]:
        """Returns rows within row limit"""

        # Gets the rows to parse
        rows: list[bs4.element.Tag] = get_tags("tr", self.URL, self.session)

        row_instances = []
        # Remove last ten rows - html is messed up
        for row in rows[: len(rows) - 10]:
            try:
                info = FrontPageInfo(row)
            # We don't support Unclassified events
            # This appears to be a bug in their website
            except KeyError:
                continue
            row_instances.append(info.RowCls(row))

        return row_instances

    def _write_csv(self, rows: list[dict[str, Any]]) -> None:
        with self.csv_path.open("w") as f:
            writer = csv.DictWriter(f, fieldnames=Row.columns)
            writer.writeheader()
            writer.writerows(rows)
