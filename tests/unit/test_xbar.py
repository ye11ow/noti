import sys
from datetime import datetime
from datetime import timedelta
from io import StringIO
from unittest.mock import MagicMock

import pytest
from dateutil.tz import tzlocal
from dateutil import parser

from noti import XbarItem, XbarPrinter, XbarSeperator
from noti import NotiConfig

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

def create_mr_details(approved, url, status, branch, title, reviews, failed_jobs):
    mr = MagicMock()
    mr.approved = approved
    mr.url = url
    mr.ci_status = status
    mr.branch = branch
    mr.title = title
    mr.reviews = reviews
    mr.failed_pipeline_jobs = failed_jobs

    return mr

def create_review(author, body):
    review = MagicMock()
    review.author = author
    review.body = body
    review.created_at = parser.parse('2020-02-02T20:20:20Z')
    review.url = "review_url"

    return review

def create_failed_job(name, url):
    job = MagicMock()
    job.name = name
    job.url = url

    return job

class TestXbarPrinter:

    @pytest.fixture
    def bp(self):
        return XbarPrinter(NotiConfig.DEFAULT_CONFIG.get('emoji'))

    def test_time_diff(self, bp):
        before = datetime.now().astimezone(tzlocal()) - timedelta(minutes=30)
        assert bp.time_diff(before) == "30 minutes ago"

        before = datetime.now().astimezone(tzlocal()) - timedelta(minutes=130)
        assert bp.time_diff(before) == "2 hours 10 minutes ago"

        before = datetime.now().astimezone(tzlocal()) - timedelta(days=2,minutes=130)
        assert bp.time_diff(before) == "2 days 2 hours ago"

        before = datetime.now().astimezone(tzlocal()) - timedelta(days=24,minutes=130)
        assert bp.time_diff(before) == "24 days ago"

        before = datetime.now().astimezone(tzlocal()) - timedelta(days=400,minutes=130)
        assert bp.time_diff(before) == "long long ago"

    def test_print_title_only(self, bp):
        bp.title('MYTITLE')
        bp._configs = []

        out = proxy_print(bp)

        assert out == 'MYTITLE\n'
        
    def test_print_no_item(self, bp):
        bp.title('MYTITLE')

        out = proxy_print(bp)

        assert out == f"MYTITLE\n---\n{XbarPrinter._default_config}\n"
        
    def test_print_with_items(self, bp):
        bp.title('MYTITLE')
        bp.append_child(XbarItem('123'))
        bp.append_child(XbarItem('456'))

        out = proxy_print(bp)

        assert out == f"MYTITLE\n---\n123\n456\n---\n{XbarPrinter._default_config}\n"
        
    def test_fatal(self, bp):
        with pytest.raises(SystemExit):
            bp.fatal('hello', 'world')
        
    def test_add_error(self, bp):
        bp.title('MYTITLE')
        bp.add_error('_error_')

        out = proxy_print(bp)

        assert out == f"MYTITLE\n---\n_error_ | color=red\n{XbarPrinter._default_config}\n"

    def test_generate_title_no_mr(self, bp):
        bp.generate_title({})

        assert bp.title() == '😃'

    def test_generate_title(self, bp):
        mrs = {}    
        mrs['test'] = [
            create_mr(3,True,'failed'),  
            create_mr(3,True,'running'), 
            create_mr(0,False,''),
            create_mr(4,False,'RANDOMSTRING')
        ]

        bp.generate_title(mrs)

        assert bp.title() == '👍2🙃1🏃1💬10'

    def test_generate_mr(self, bp):
        mr = create_mr_details(True, 'myurl', 'success', 'mybranch', 'mytitle', [], [])

        bp.generate_mr(mr)
        items = bp._children()

        assert len(items) == 2
        assert str(items[0]) == str(XbarItem("mybranch 👍").color("green").link("myurl"))
        assert str(items[1]) == str(XbarItem("mytitle").color("white").alternate(True))

    def test_generate_mr_with_reviews_and_failed_job(self, bp):
        reviews = [
            create_review('author1', 'body1')
        ]

        failed_jobs = [
            create_failed_job('name1', 'url1')
        ]

        mr = create_mr_details(False, 'myurl', 'failed', 'mybranch', 'mytitle', reviews, failed_jobs)

        bp.generate_mr(mr)
        items = bp._children()

        assert len(items) == 2

        sub_children = items[0]._children

        assert len(sub_children) == 5
        assert str(sub_children[0]) == str(XbarItem("--Failed jobs"))
        assert str(sub_children[1]) == str(XbarItem("--name1").color("red").link("url1"))
        assert isinstance(sub_children[2], XbarSeperator)
        assert str(sub_children[3]) == str(XbarItem("--Discussions (long long ago)"))
        assert str(sub_children[4]) == str(XbarItem("--author1: body1").link("review_url").length(32))

        assert str(items[0]).startswith('mybranch 💬1')
        assert str(items[1]) == str(XbarItem("mytitle").color("white").alternate(True))
