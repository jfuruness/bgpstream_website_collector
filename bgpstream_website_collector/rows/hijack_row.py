# type: ignore

from typing import Any

import bs4

from .row import Row


class HijackRow(Row):
    """Class for parsing Hijack events. Inherits from Row."""

    name: str = "Possible Hijack"

    def _parse_uncommon_info(
        self,
        as_info: Any,
        extended_children: list[bs4.element.Tag],
    ) -> None:
        """Parses misc hijack row info."""

        (
            self._data["hijack_expected_origin_name"],
            self._data["hijack_expected_origin_number"],
        ) = self._parse_as_info(as_info[1])
        (
            self._data["hijack_detected_origin_name"],
            self._data["hijack_detected_origin_number"],
        ) = self._parse_as_info(as_info[3])
        # We must work from the end of the elements, because the number
        # of elements at the beginning may vary depending on whether or not
        # end time is specified
        end = len(extended_children)
        # Note: Group 1 because group 0 returns the entire string,
        # not the captured regex
        self._data["hijack_expected_prefix"] = (
            self._ip_regex.search(extended_children[end - 6].string).group(1).strip()
        )
        self._data["hijack_more_specific_prefix"] = (
            self._ip_regex.search(extended_children[end - 4].string).group(1).strip()
        )

        self._data["hijack_detected_as_path"] = self._nums_regex.search(
            extended_children[end - 2].string.strip()
        ).group(1)
        self._data["hijack_detected_as_path"] = str(
            [int(s) for s in self._data.get("hijack_detected_as_path").split(" ")]
        )
        self._data["hijack_detected_as_path"] = (
            self._data.get("hijack_detected_as_path")
            .replace("[", "{")
            .replace("]", "}")
        )

        self._data["hijack_detected_by_bgpmon_peers"] = self._nums_regex.search(
            extended_children[end - 1].string.strip()
        ).group(1)
