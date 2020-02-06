import sys
from datetime import datetime
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from dateutil.tz import tzlocal

from noti import BitbarPrinter

def proxy_print(bp):
    saved_stdout = sys.stdout
    out = StringIO()
    sys.stdout = out
    bp.print()
    sys.stdout = saved_stdout

    return out.getvalue()

class TestBitbarPrinter:

    def test_time_diff(self):
        b = BitbarPrinter()
        before = datetime.now().astimezone(tzlocal()) - timedelta(minutes=30)
        assert b.time_diff(before) == "30 minutes ago"

        before = datetime.now().astimezone(tzlocal()) - timedelta(minutes=130)
        assert b.time_diff(before) == "2 hours 10 minutes ago"

    def test_print_title_only(self):
        b = BitbarPrinter()
        b.title('MYTITLE')
        b._configs = []

        out = proxy_print(b)

        assert out == 'MYTITLE\n'
        
    def test_print_no_item(self):
        b = BitbarPrinter()
        b.title('MYTITLE')

        out = proxy_print(b)

        assert out == 'MYTITLE\n---\nConfigure noti | bash="vi $HOME/.noticonfig.json"\n'
        
    def test_print_with_items(self):
        b = BitbarPrinter()
        b.title('MYTITLE')
        b.add('123')
        b.add('456')

        out = proxy_print(b)

        assert out == 'MYTITLE\n---\n123\n456\n---\nConfigure noti | bash="vi $HOME/.noticonfig.json"\n'
        
    def test_print_error(self):
        b = BitbarPrinter()

        with pytest.raises(SystemExit):
            b.print_error('hello', 'world')
