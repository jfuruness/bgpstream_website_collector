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
        file_funcs.write_dicts_to_tsv(tsv_rows, self.tsv_path)
        logging.debug("Wrote TSV")

    def _get_rows(self) -> List[Row]:
        """Returns rows within row limit"""

        if self.debug:
            row_limit = 30

        # Gets the rows to parse
        rows: List[bs4.element.Tag] = helper_funcs.get_tags(self.url, "tr")
        # Reduce/set row_limit to total number of rows
        # We remove last ten rows because html is messed up
        if row_limit is None or row_limit > len(rows) - 10:
            row_limit = len(rows) - 10

        row_instances = []
        for row in rows[:row_limit]:
            row_front_page_info = FrontPageInfo(row)
            row_instances.append(row_front_page_info.RowCls(row, self.url))

        return row_instances
