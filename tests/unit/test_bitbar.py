from datetime import datetime
from datetime import timedelta

from dateutil.tz import tzlocal

from noti import BitbarPrinter

class TestBitbarPrinter:

    def test_time_diff(self):
        b = BitbarPrinter()
        before = datetime.now().astimezone(tzlocal()) - timedelta(minutes=30)
        assert b.time_diff(before) == "30 minutes ago"

        before = datetime.now().astimezone(tzlocal()) - timedelta(minutes=130)
        assert b.time_diff(before) == "2 hours 10 minutes ago"