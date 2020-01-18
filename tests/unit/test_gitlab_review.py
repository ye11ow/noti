from unittest.mock import MagicMock

from noti import GitlabReview

class TestGitlabReview:

    def test_author(self):
        mock_review = MagicMock()
        mock_review.attributes.get.return_value = {
            'name': 'myauthor'
        }
        review = GitlabReview({}, mock_review)

        assert review.author == 'myauthor'
        mock_review.attributes.get.assert_called_with('author')

    def test_created_at(self):
        mock_review = MagicMock()
        mock_review.attributes.get.return_value = '2013-09-30T13:46:01Z'
        review = GitlabReview({}, mock_review)

        created_at = review.created_at
        
        assert created_at.year == 2013
        assert created_at.month == 9
        assert created_at.day == 30
        mock_review.attributes.get.assert_called_with('created_at')

    def test_body(self):
        mock_review = MagicMock()
        mock_review.attributes.get.return_value = 'mybody'
        review = GitlabReview({}, mock_review)
        
        assert review.body == 'mybody'
        mock_review.attributes.get.assert_called_with('body')

    def test_url(self):
        mock_review = MagicMock()
        mock_review.get_id.return_value = '1234567'

        mock_mr = MagicMock()
        mock_mr.url = 'https://example.com/mr'
        review = GitlabReview(mock_mr, mock_review)

        assert review.url == 'https://example.com/mr#note_1234567'
