import csv
from datetime import date
from pathlib import Path
from typing import Optional

import bs4
import requests_cache
from tqdm import tqdm

from .front_page_info import FrontPageInfo
from .row import Row
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

    def __del__(self):
        self.session.close()

    def run(self) -> None:
        """Inserts info from bgpstream.com into a csv"""

        csv_rows = []
        # Parses rows if they are the event types desired
        rows: list[Row] = self._get_rows()
        for row in tqdm(rows, desc="Parsing BGPStream.com", total=len(rows)):
            # Parses the row into csv format. Can't do with mp, rate limited
            csv_rows.append(row.parse())
        self._write_csv(csv_rows)

    def _get_rows(self) -> list[Row]:
        """Returns rows within row limit"""

        # Gets the rows to parse
        rows: list[bs4.element.Tag] = get_tags("tr", self.URL, self.session)

        row_instances = []
        # Remove last ten rows - html is messed up
        for row in rows[:len(rows) - 10]:
            try:
                info = FrontPageInfo(row)
            # We don't support Unclassified events
            # This appears to be a bug in their website
            except KeyError:
                continue
            row_instances.append(info.RowCls(row))

        return row_instances

    def _write_csv(self, rows: list[Row]) -> None:
        with self.csv_path.open("w") as f:
            writer = csv.DictWriter(f, fieldnames=Row.columns)
            writer.writeheader()
            writer.writerows(rows)
