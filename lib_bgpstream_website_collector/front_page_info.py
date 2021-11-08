from dataclasses import dataclass

import bs4

from .row import Row


@dataclass(frozen=True)
class FrontPageInfo:
    event_name: str
    start: str
    end: str
    url: str
    event_num: int
    end: str
    RowCls: Row

    def __post_init__(self, row: bs4.element.Tag, url: str):
        """Returns type of event, start, end, url, event num.

        Essentially, all info available on front page of bgpstream.com.
        """

        # Gets the type of event (in the events enum) for the row
        self.event_name: str = [x for x in row.children][1].string.strip()

        self.start = [x for x in row.children][7].string.strip() + '+00:00'
        self.end: str = [x for x in row.children][9].string.strip() + '+00:00'
        self.url: str = [x for x in row.children][11].a["href"]
        self.event_num: int = int(url.split("/")[-1])
        if self.end == "+00:00":
            self.end = 'None'

        self.RowCls = Row.name_to_type[self.event_name]
