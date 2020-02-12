from unittest.mock import MagicMock
import pytest

from noti import GitlabReview

class DummyReview:
    def __init__(self, author, created_at, body, id):
        self.attributes = {
            'author': {
                'name': author
            },
            'created_at': created_at,
            'body': body
        }
        self._id = id

    def get_id(self):
        return self._id

class DummyMR:
    def __init__(self, url):
        self._url = url

    @property
    def url(self):
        return self._url

class TestGitlabReview:

    @pytest.fixture(autouse=True)
    def review(self):
        dr = DummyReview('myauthor', "2013-09-30T13:46:01Z", 'mybody', '1234567')
        dmr = DummyMR('https://example.com/mr')
        
        return GitlabReview(dmr, dr)

    def test_author(self, review):
        assert review.author == 'myauthor'

    def test_created_at(self, review):
        created_at = review.created_at
        
        assert created_at.year == 2013
        assert created_at.month == 9
        assert created_at.day == 30

    def test_body(self, review):        
        assert review.body == 'mybody'

    def test_url(self, review):
        assert review.url == 'https://example.com/mr#note_1234567'
