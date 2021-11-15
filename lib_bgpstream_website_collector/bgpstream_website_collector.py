from copy import deepcopy
import csv
import logging
from typing import List

import bs4
from ipaddress import ip_network
from tqdm import tqdm

from lib_roa_checker import ROAChecker
from lib_roa_collector import ROACollector
from lib_utils import file_funcs, helper_funcs, base_classes

from .front_page_info import FrontPageInfo
from .row import Row


class BGPStreamWebsiteCollector(base_classes.Base):
    """This class parses bgpstream.com information"""

    url = "https://bgpstream.com"

    def run(self):
        """Inserts info from bgpstream.com into a tsv"""

        roa_checker = self._get_roa_checker()
        tsv_rows = []
        # Parses rows if they are the event types desired
        rows: List[Row] = self._get_rows()
        for row in tqdm(rows, desc="Parsing BGPStream.com", total=len(rows)):
            # Parses the row into tsv format. Can't do with mp, rate limited
            tsv_rows.append(row.parse(roa_checker))
        file_funcs.write_dicts_to_tsv(tsv_rows, self.tsv_path, cols=Row.columns)
        logging.debug("Wrote TSV")
        if len(tsv_rows) == 0:
            print(f"No bgpstream.com events for {self.dl_time}")

    def _get_roa_checker(self):
        """ROA checker.

        We can get the roa based on the prefix, so we do this in advance
        Afterwards we want fast lookups based on just the origin
        so we construct a dict for this
        """

        kwargs = deepcopy(self.kwargs)
        kwargs["dir_"] = self.dir_ / ROACollector.__name__
        roa_collector = ROACollector(**kwargs)
        roa_collector.run()

        roa_checker = ROAChecker()
        with open(roa_collector.tsv_path, mode="r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                origin = int(row["asn"])
                try:
                    max_length = int(row["max_length"])
                # Sometimes max length is nan
                except ValueError:
                    max_length = None
                roa_checker.insert(ip_network(row["prefix"]), origin, max_length)
        return roa_checker


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
