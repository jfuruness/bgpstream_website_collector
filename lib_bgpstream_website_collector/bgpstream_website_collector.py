import logging
from typing import List

import bs4
from tqdm import tqdm

from lib_utils import file_funcs, helper_funcs, base_classes

from .front_page_info import FrontPageInfo
from .row import Row


class BGPStreamWebsiteCollector(base_classes.Base):
    """This class parses bgpstream.com information"""

    url = "https://bgpstream.com"

    def run(self):
        """Inserts info from bgpstream.com into a tsv"""

        tsv_rows = []
        # Parses rows if they are the event types desired
        rows: List[Row] = self._get_rows()
        for row in tqdm(rows, desc="Parsing BGPStream.com", total=len(rows)):
            # Parses the row into tsv format. Can't do with mp, rate limited
            tsv_rows.append(row.parse())
        if len(tsv_row) > 0:
            file_funcs.write_dicts_to_tsv(tsv_rows, self.tsv_path)
            logging.debug("Wrote TSV")

    def _get_rows(self) -> List[Row]:
        """Returns rows within row limit"""

        # Gets the rows to parse
        rows: List[bs4.element.Tag] = helper_funcs.get_tags(self.url, "tr")

        row_instances = []
        # Remove last ten rows - html is messed up
        for row in rows[:len(rows) - 10]:
            try:
                info = FrontPageInfo(row)
            # We don't support Unclassified events
            # This appears to be a bug in their website
            except KeyError:
                continue
            if info.start_date <= self.dl_time.date() <= info.end_date:
                row_instances.append(info.RowCls(row))

        return row_instances
