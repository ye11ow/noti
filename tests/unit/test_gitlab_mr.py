from unittest.mock import MagicMock

from noti import GitlabMR

class TestGitlabMR:

    def test_ci_failed(self):
        mock_mr = MagicMock()
        mock_mr.attributes.get.return_value = {
            'status': 'failed'
        }

        review = GitlabMR({}, mock_mr)

        assert review.ci_failed
        mock_mr.attributes.get.assert_called_with('pipeline')

    def test_approved(self):
        mock_mr = MagicMock()
        mock_mr.approvals.get.return_value.attributes.get.return_value = True

        review = GitlabMR({}, mock_mr)
        assert review.approved
        mock_mr.approvals.get.return_value.attributes.get.assert_called_with('approved')
        