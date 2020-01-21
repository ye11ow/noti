from unittest.mock import MagicMock
from unittest.mock import patch
import pytest

from noti import Gitlab
from noti import NotiError

class TestGitlab:

    @pytest.fixture(autouse=True)
    def config(self):
        return {
            "gitlab": {
                "token": "fake",
                "project_id": [1],
                "host": "https://example.com"
            }
        }

    def test_init(self, config):
        g = Gitlab(config)
        assert g != None

    def test_init_with_wrong_config(self):
        config = {
            "gitlab": {
                "token": "",
                "project_id": [1],
                "host": ""
            }
        }
        with pytest.raises(NotiError):
            g = Gitlab(config)

    @patch('gitlab.Gitlab')
    def test_get_mrs(self, mock_gl, config):
        project = MagicMock()
        mock_gl.return_value.projects.get.return_value = project
        project.mergerequests.list.return_value = [MagicMock(), MagicMock(), MagicMock()]

        g = Gitlab(config)
        mrs = g.get_mrs()

        assert len(mrs) == 3
        project.mergerequests.list.assert_called_with(state='opened')