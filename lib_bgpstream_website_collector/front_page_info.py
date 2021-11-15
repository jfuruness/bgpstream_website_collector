from dataclasses import dataclass
from datetime import datetime, date, timedelta

import bs4

from .row import Row


@dataclass(init=False)
class FrontPageInfo:
    event_name: str
    start: str
    start_date: date
    end: str
    end_date: date
    url: str
    event_num: int
    end: str
    RowCls: Row

    def __init__(self, row: bs4.element.Tag):
        """Returns type of event, start, end, url, event num.

        Essentially, all info available on front page of bgpstream.com.
        """

        # Gets the type of event (in the events enum) for the row
        self.event_name: str = [x for x in row.children][1].string.strip()

        self.start = [x for x in row.children][7].string.strip() + '+00:00'
        self.start_date = datetime.strptime(self.start.split(" ")[0], "%Y-%m-%d").date()
        self.end: str = [x for x in row.children][9].string.strip() + '+00:00'
        self.url: str = [x for x in row.children][11].a["href"]
        self.event_num: int = int(self.url.split("/")[-1])
        if self.end == "+00:00":
            self.end = 'None'
            self.end_date = self.start_date + timedelta(days=1)
        else:
            self.end_date = datetime.strptime(self.end.split(" ")[0], "%Y-%m-%d").date()

        self.RowCls = Row.name_to_type[self.event_name]
