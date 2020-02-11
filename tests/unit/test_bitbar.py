import sys
from datetime import datetime
from datetime import timedelta
from io import StringIO
from unittest.mock import patch
from unittest.mock import MagicMock

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

def create_mr(reviews, approved, status):
    mr = MagicMock()
    mr.reviews = []
    for i in range(reviews):
        mr.reviews.append('x')

    mr.approved = approved
    mr.ci_status = status

    return mr

def create_mr_details(approved, url, status, branch, title, reviews):
    mr = MagicMock()
    mr.approved = approved
    mr.url = url
    mr.ci_status = status
    mr.branch = branch
    mr.title = title
    mr.reviews = reviews

    return mr

def create_review(author, body):
    review = MagicMock()
    review.author = author
    review.body = body

    return review

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

    def test_generate_title_no_mr(self):
        b = BitbarPrinter()

        b.generate_title({})

        assert b._title == '😃'

    def test_generate_title(self):
        b = BitbarPrinter()

        mrs = {}    
        mrs['test'] = [
            create_mr(3,True,'failed'),  
            create_mr(3,True,'running'), 
            create_mr(0,False,''),
            create_mr(4,False,'RANDOMSTRING')
        ]

        b.generate_title(mrs)

        assert b._title == '👍2🙃1🏃1💬10'

    def test_generate_mr(self):
        b = BitbarPrinter()

        mr = create_mr_details(True, 'myurl', 'success', 'mybranch', 'mytitle', [])

        b.generate_mr(mr)

        assert b._items[0] == 'mybranch  👍 | href=myurl color=green\n\n\n'
        assert b._items[1] == 'mytitle | alternate=true'

    def test_generate_mr_with_reviews(self):
        b = BitbarPrinter()

        reviews = [
            create_review('author1', 'body1')
        ]

        mr = create_mr_details(False, 'myurl', 'success', 'mybranch', 'mytitle', reviews)

        b.generate_mr(mr)

        # TODO: improve the assertion here
        assert b._items[0].startswith('mybranch 💬1')
        assert b._items[1] == 'mytitle | alternate=true'
