from unittest.mock import MagicMock
from unittest.mock import patch
from requests.exceptions import ConnectionError
import pytest

from noti import main

class TestNoti:

    @pytest.fixture
    def bp(self):
        return MagicMock()
    
    @pytest.fixture
    def conf(self):
        return MagicMock()

    def test_no_vcs(self, conf, bp):
        conf.init_vcs.return_value = []

        main(conf, bp)

        assert bp.print_error.assert_called

    def test_no_connection(self, conf, bp):
        vcs = MagicMock()
        vcs.get_mrs.side_effect = ConnectionError()
        conf.init_vcs.return_value = [vcs]

        main(conf, bp)

        assert bp.print_error.assert_called

    def test_happy_path(self, conf, bp):
        vcs = MagicMock()
        mrs = {
            '_repo_': [
                '_mr_',
                '_mr_'
            ]
        }
        vcs.get_mrs.return_value = mrs
        conf.init_vcs.return_value = [vcs]
        
        main(conf, bp)

        bp.generate_title.assert_called_with(mrs) 
        bp.add.assert_called_with('_repo_')
        bp.generate_mr.assert_called_with('_mr_')
        bp.print.assert_called()
