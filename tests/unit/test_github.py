from unittest.mock import MagicMock
from unittest.mock import patch
import pytest

from noti import Github
from noti import NotiError

def build_mr_with_username(username): 
    mr = MagicMock()
    mr.user.login = username
    return mr

class TestGithub:

    @pytest.fixture
    def config(self):
        return {
            'token': '_token_',
            'repo': ['_repo_'],
            'host': '_host_',
            'mr_limit': 10
        }

    @pytest.fixture
    def wrong_config(self):
        return {
            'token': '',
            'repo': ['_repo_'],
            'host': ''
        }
    
    @pytest.fixture
    def config_with_filter(self):
        return {
            'token': '_token_',
            'repo': ['_repo_'],
            'host': '_host_',
            'mr_limit': 10,
            "filters": {
                "usernames": ["test1", "test2"]
            }
        }

    @patch('github.Github')
    def test_init(self, mock_gh, config):
        g = Github(config)
        mock_gh.assert_called_with(config.get('token'), base_url=config.get('host'), per_page=config.get('mr_limit'))
        assert g != None

    def test_init_with_wrong_config(self, wrong_config):
        with pytest.raises(NotiError):
            g = Github(wrong_config)

    @patch('github.Github')
    def test_get_mrs(self, mock_gh, config):
        repo = MagicMock()
        mock_gh.return_value.get_repo.return_value = repo
        repo.get_pulls.return_value.get_page.return_value = [MagicMock(), MagicMock(), MagicMock()]

        g = Github(config)
        mrs = g.get_mrs()

        assert len(mrs['_repo_']) == 3
        mock_gh.return_value.get_repo.assert_called_with('_repo_')
        repo.get_pulls.assert_called_with(state='open', sort='created', base='main')

    @patch('github.Github')
    def test_get_mrs_with_filter(self, mock_gh, config_with_filter):
        repo = MagicMock()
        mock_gh.return_value.get_repo.return_value = repo
        repo.get_pulls.return_value.get_page.return_value = [
            build_mr_with_username('test1'), 
            build_mr_with_username('test2'),  
            build_mr_with_username('test3')
        ]

        g = Github(config_with_filter)
        mrs = g.get_mrs()

        assert len(mrs['_repo_']) == 2
        mock_gh.return_value.get_repo.assert_called_with('_repo_')
        repo.get_pulls.assert_called_with(state='open', sort='created', base='main')