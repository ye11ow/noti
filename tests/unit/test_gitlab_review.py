from unittest.mock import MagicMock
import pytest

from noti import GitlabReview
from fixtures import gitlab as mock

class TestGitlabReview:

    @pytest.fixture
    def review(self):
        return GitlabReview(MagicMock(), mock.DummyReview())

    def test_author(self, review):
        assert review.author == '_author_'

    def test_created_at(self, review):
        created_at = review.created_at
        
        assert created_at.year == 2020
        assert created_at.month == 2
        assert created_at.day == 2

    def test_body(self, review):        
        assert review.body == '_body_'

    def test_url(self, review):
        review._mr.url = '_url_'
        assert review.url == '_url_#note__id_'
