from unittest.mock import MagicMock
import pytest

from noti import GitlabMR

class TestGitlabMR:

    @pytest.fixture(autouse=True)
    def mr(self):
        return GitlabMR({}, MagicMock())

    def test_ci_failed(self, mr):
        mr._mr.attributes.get.return_value = {
            'status': 'failed'
        }

        assert mr.ci_failed
        mr._mr.attributes.get.assert_called_with('pipeline')

    def test_approved(self, mr):
        mr._mr.approvals.get.return_value.attributes.get.return_value = True

        assert mr.approved
        mr._mr.approvals.get.return_value.attributes.get.assert_called_with('approved')
        