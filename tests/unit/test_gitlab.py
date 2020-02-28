from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from noti import Gitlab
from noti import NotiError

class TestGitlab:

    @pytest.fixture(autouse=True)
    def config(self):
        return {
            "token": "fake",
            "project_id": [1],
            "host": "https://example.com",
            "mr_limit": 5
        }

    def test_init(self, config):
        g = Gitlab(config)
        assert g != None

    def test_init_with_wrong_config(self):
        config = {
            "token": "",
            "project_id": [1],
            "host": ""
        }
        with pytest.raises(NotiError):
            g = Gitlab(config)

    @patch('gitlab.Gitlab')
    def test_get_mrs(self, mock_gl, config):
        project = MagicMock()
        mock_gl.return_value.projects.get.return_value = project
        project.mergerequests.list.return_value = [MagicMock(), MagicMock(), MagicMock()]
        project.attributes.get.return_value = 'test_repo'

        g = Gitlab(config)
        mrs = g.get_mrs()

        assert 'test_repo' in mrs
        project.attributes.get.assert_called_with('name')
        assert len(mrs['test_repo']) == 3
        project.mergerequests.list.assert_called_with(state='opened', per_page=5)