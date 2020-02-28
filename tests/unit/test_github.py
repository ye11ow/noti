from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from noti import Github
from noti import NotiError

class TestGithub:

    @pytest.fixture
    def config(self):
        return {
            'token': 'fake',
            'repo': ['_repo_'],
            'host': 'https://example.com',
            'mr_limit': 5
        }

    def test_init(self, config):
        g = Github(config)
        assert g != None

    def test_init_with_wrong_config(self):
        config = {
            'token': '',
            'repo': ['_repo_'],
            'host': ''
        }
        with pytest.raises(NotiError):
            g = Github(config)

    @patch('github.Github')
    def test_get_mrs(self, mock_gh, config):
        repo = MagicMock()
        mock_gh.return_value.get_repo.return_value = repo
        repo.get_pulls.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]

        g = Github(config)
        mrs = g.get_mrs()

        assert len(mrs['_repo_']) == config.get('mr_limit')
        mock_gh.return_value.get_repo.assert_called_with('_repo_')
        repo.get_pulls.assert_called_with(state='open', sort='created', base='master')