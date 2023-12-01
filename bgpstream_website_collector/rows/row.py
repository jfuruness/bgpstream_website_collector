from abc import ABC, abstractmethod
import re
from typing import Any, Optional

import bs4
from requests_cache import CachedSession

from ..utils import get_tags


class Row(ABC):
    """Parent Class for parsing rows of bgpstream.com"""

    # This regex parses out the AS number and name from a string of both
    _as_regex = re.compile(
        r"""
                           (?P<as_name>.+?)\s\(
                           AS\s(?P<as_number>\d+)\)
                           |
                           (?P<as_number2>\d+).*?\((?P<as_name2>.+?)\)
                           """,
        re.VERBOSE,
    )
    # This regex returns a string that starts and ends with numbers
    _nums_regex = re.compile(r"(\d[^a-zA-Z\(\)\%]*\d*)")
    # This regex is used in some places to get prefixes
    _ip_regex = re.compile(r".+?:(.+)")

    # I know that these are distinct things
    # Maybe you think they should only be in separate files
    # But for our use case, we only ever use them in aggregate

    # Common fields first
    # DO NOT ALTER THE ORDERING!!!
    columns = (
        "country",
        "start_time",
        "end_time",
        "event_number",
        "event_type",
        "url",
        # Hijack fields
        "hijack_detected_as_path",
        "hijack_detected_by_bgpmon_peers",
        "hijack_detected_origin_name",
        "hijack_detected_origin_number",
        "hijack_expected_origin_name",
        "hijack_expected_origin_number",
        "hijack_expected_prefix",
        "hijack_more_specific_prefix",
        # Leak fields
        "leak_detected_by_bgpmon_peers",
        "leak_example_as_path",
        "leaked_prefix",
        "leaked_to_name",
        "leaked_to_number",
        "leaker_as_name",
        "leaker_as_number",
        "leak_origin_as_name",
        "leak_origin_as_number",
        # Outage fields
        "outage_as_name",
        "outage_as_number",
        "outage_number_prefixes_affected",
        "outage_percent_prefixes_affected",
    )
    name_to_type: dict[str, type["Row"]] = dict()

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        # mypy just doesn't get this
        cls.name_to_type[cls.name] = cls  # type: ignore

    def __init__(self, row: bs4.element.Tag):
        self.el = row

    def parse(self, session: CachedSession) -> dict[str, Any]:
        """Parses, formats, and appends a row of data from bgpstream.com.

        For a more in depth explanation see the top of the file."""

        # Initializes the temporary row
        self._data: dict[str, Any] = dict()
        # Gets the common elements and stores them in temp_row
        # Gets the html of the page for that specific event
        try:
            as_info, extended_children = self._parse_common_elements(session)
            # Parses uncommon elements and stores them in temp_row
            self._parse_uncommon_info(as_info, extended_children)
        except AttributeError:
            print("ERROR IN THIS ROW. WILL NOT BE APPENDED")

        return self.tsv_formatted_data()

    def tsv_formatted_data(self) -> dict[str, Any]:
        for k, v in self._data.items():
            assert k in self.columns, k

        return {col: self._data.get(col) for col in self.columns}

    ####################
    # Helper Functions #
    ####################

    def _parse_common_elements(
        self, session: CachedSession
    ) -> tuple[Any, list[bs4.element.Tag]]:
        """Parses common tags and adds data to temp_row.

        All common elements on the initial page are parsed, then the
        html for the url for that event in that row is retrieved. For a
        more in depth explanation please see the top of the file.

        The first return value is the list of strings for as_info.
        The second return value is a list of more tags to parse.
        """

        children = [x for x in self.el.children]
        # Even with assertions, mypy doesn't get that these are navigable strings
        self._data = {"event_type": children[1].string.strip()}  # type: ignore
        # Must use stripped strings here because the text contains an image
        self._data["country"] = " ".join(children[3].stripped_strings)  # type: ignore
        try:
            # If there is just one string this will work
            as_info = children[5].string.strip()  # type: ignore
        except AttributeError:
            # If there is more than one AS this will work
            stripped = children[5].stripped_strings  # type: ignore
            as_info = [x for x in stripped]
        # Gets common elements
        self._data["start_time"] = children[7].string.strip()  # type: ignore
        self._data["end_time"] = children[9].string.strip()  # type: ignore
        self._data["url"] = children[11].a["href"]  # type: ignore
        item = self._nums_regex.search(self._data["url"])
        assert item, "mypy"
        self._data["event_number"] = item.group()
        url = "https://bgpstream.com" + self._data["url"]

        # Returns the as info and html for the page with more info
        return as_info, get_tags("td", url, session)

    # mypy doesn't see that this has a return statement
    def _parse_as_info(  # type: ignore
        self, as_info: Any
    ) -> tuple[Optional[str], Optional[str]]:
        """Performs regex on as_info to return AS number and AS name.

        This is a mess, but that's because parsing html is a mess.
        """

        assert isinstance(as_info, str)
        as_parsed = self._as_regex.search(as_info)

        # If the as_info is "N/A" and the regex returns nothing
        if as_parsed is None:
            # Sometimes we can get this
            try:
                return None, re.findall(r"\d+", as_info)[0]
            # Sometimes not
            except IndexError:  # Should not use bare except
                return None, None
        else:
            # This is the first way the string can be formatted:
            if as_parsed.group("as_number") not in [None, "", " "]:
                return as_parsed.group("as_name"), as_parsed.group("as_number")
            # This is the second way the string can be formatted:
            elif as_parsed.group("as_number2") not in [None, "", " "]:
                return as_parsed.group("as_name2"), as_parsed.group("as_number2")

    @abstractmethod
    def _parse_uncommon_info(
        self,
        as_info: Any,
        extended_children: list[bs4.element.Tag],
    ) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
