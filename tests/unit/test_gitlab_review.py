from unittest.mock import MagicMock
import pytest

from noti import GitlabReview

class TestGitlabReview:

    @pytest.fixture(autouse=True)
    def review(self):
        return GitlabReview(MagicMock(), MagicMock())

    def test_author(self, review):
        review._review.attributes.get.return_value = {
            'name': 'myauthor'
        }

        assert review.author == 'myauthor'
        review._review.attributes.get.assert_called_with('author')

    def test_created_at(self, review):
        review._review.attributes.get.return_value = '2013-09-30T13:46:01Z'

        created_at = review.created_at
        
        assert created_at.year == 2013
        assert created_at.month == 9
        assert created_at.day == 30
        review._review.attributes.get.assert_called_with('created_at')

    def test_body(self, review):
        review._review.attributes.get.return_value = 'mybody'
        
        assert review.body == 'mybody'
        review._review.attributes.get.assert_called_with('body')

    def test_url(self, review):
        review._review.get_id.return_value = '1234567'
        review._mr.url = 'https://example.com/mr'

        assert review.url == 'https://example.com/mr#note_1234567'
