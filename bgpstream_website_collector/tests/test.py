import csv
from pathlib import Path
from unittest.mock import patch

from bgpstream_website_collector import BGPStreamWebsiteCollector
from bgpstream_website_collector import LeakRow, HijackRow, OutageRow


class TestBGPStreamWebsiteCollector:
    def test_run(self, tmp_path: Path) -> None:
        """Tests the run func of bgpstream website collector

        Since this takes a LONG time, we just patch to get one of each type of Row
        And really this should be more comprehensive, but this will do for now
        """

        csv_path = tmp_path / "bgpstream.csv"
        requests_cache_db_path = tmp_path / "requests_cache.db"

        original_get_rows = BGPStreamWebsiteCollector._get_rows

        def mock_get_rows(*args, **kwargs):
            original_function = original_get_rows
            full_list = original_function(*args, **kwargs)
            shortened_list = list()
            for RowCls in (HijackRow, LeakRow, OutageRow):
                for row in full_list:
                    if isinstance(row, RowCls):
                        shortened_list.append(row)
                        break
            return shortened_list

        with patch(
            "bgpstream_website_collector.BGPStreamWebsiteCollector._get_rows",
            new=mock_get_rows,
        ):
            parser = BGPStreamWebsiteCollector(
                csv_path=csv_path, requests_cache_db_path=requests_cache_db_path
            )
            rows = parser.run()
            assert len(rows) == 3
            with csv_path.open() as f:
                csv_rows = [dict(x) for x in csv.DictReader(f)]
                assert len(csv_rows) == len(rows)
