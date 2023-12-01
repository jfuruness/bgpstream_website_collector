# type: ignore

# even with asserts, mypy doesn't understand these types

from typing import Any

import bs4

from .row import Row


class OutageRow(Row):
    """Class for parsing outage events"""

    name: str = "Outage"

    def _parse_uncommon_info(
        self,
        as_info: Any,
        extended_children: list[bs4.element.Tag],
    ) -> None:
        """Parses misc outage row info."""

        (
            self._data["outage_as_name"],
            self._data["outage_as_number"],
        ) = self._parse_as_info(as_info)
        # We must work from the end of the elements, because the number
        # of elements at the beginning may vary depending on whether or not
        # end time is specified
        prefix_string = extended_children[len(extended_children) - 1].string.strip()
        # Finds all the numbers within a string
        prefix_info = self._nums_regex.findall(prefix_string)
        self._data["outage_number_prefixes_affected"] = prefix_info[0].strip()
        self._data["outage_percent_prefixes_affected"] = prefix_info[1].strip()
