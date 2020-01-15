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
    
    def test_body(self):
        mock_review = MagicMock()
        mock_review.attributes.get.return_value = 'mybody'
        review = GitlabReview({}, mock_review)
        
        assert review.body == 'mybody'