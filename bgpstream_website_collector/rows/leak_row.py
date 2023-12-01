# type: ignore

# even with asserts, mypy doesn't understand these types


from typing import Any

import bs4

from .row import Row


class LeakRow(Row):
    """Class for parsing Leak events. Inherits from Row."""

    name: str = "BGP Leak"

    def _parse_uncommon_info(
        self,
        as_info: Any,
        extended_children: list[bs4.element.Tag],
    ) -> None:
        """Parses misc leak row info."""

        (
            self._data["leak_origin_as_name"],
            self._data["leak_origin_as_number"],
        ) = self._parse_as_info(as_info[1])
        (
            self._data["leaker_as_name"],
            self._data["leaker_as_number"],
        ) = self._parse_as_info(as_info[3])
        # We must work from the end of the elements, because the number
        # of elements at the beginning may vary depending on whether or not
        # end time is specified
        end = len(extended_children)
        # Note: Group 1 because group 0 returns the entire string,
        # not the captured regex
        self._data["leaked_prefix"] = (
            self._nums_regex.search(extended_children[end - 5].string.strip())
            .group(1)
            .rstrip()
        )
        leaked_to_info = [x for x in extended_children[end - 3].stripped_strings]
        # We use arrays here because there could be several AS's
        self._data["leaked_to_number"] = []
        self._data["leaked_to_name"] = []
        # We start the range at 1 because 0 returns the string: "leaked to:"
        for i in range(1, len(leaked_to_info)):
            name, number = self._parse_as_info(leaked_to_info[i])
            self._data["leaked_to_number"].append(int(number))
            self._data["leaked_to_name"].append(name)
        self._data["leaked_to_number"] = (
            str(self._data.get("leaked_to_number")).replace("[", "{").replace("]", "}")
        )
        self._data["leaked_to_name"] = (
            str(self._data.get("leaked_to_name")).replace("[", "{").replace("]", "}")
        )
        example_as_path = self._nums_regex.search(
            extended_children[end - 2].string.strip()
        ).group(1)
        example_as_path = str([int(s) for s in example_as_path.split(" ")])
        self._data["leak_example_as_path"] = example_as_path.replace("[", "{").replace(
            "]", "}"
        )
        self._data["leak_detected_by_bgpmon_peers"] = self._nums_regex.search(
            extended_children[end - 1].string.strip()
        ).group(1)
