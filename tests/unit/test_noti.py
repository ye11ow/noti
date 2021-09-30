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
    def vcs(self):
        vcs = MagicMock()
        vcs.name = '_name_'
        vcs.return_value.name = '_name_'

        return vcs
    
    @pytest.fixture
    def conf(self):
        conf = MagicMock()
        conf.user_config = {
            '_name_': {}
        }

        return conf
    def test_no_vcs(self, bp):
        main([], {}, bp)

        bp.fatal.assert_called

    def test_no_connection(self, bp, vcs, conf):
        vcs.return_value.get_mrs.side_effect = ConnectionError()

        main([vcs], conf, bp)

        conf.get_config.assert_called_with('_name_')
        bp.add_error.assert_called_with('_name_: failed to connect to the server')

    def test_happy_path(self, bp, vcs, conf):
        mrs = {
            '_repo_': [
                '_mr_',
                '_mr_'
            ]
        }
        vcs.return_value.get_mrs.return_value = mrs
        
        main([vcs], conf, bp)

        bp.generate_title.assert_called_with(mrs) 
        bp.generate_mr.assert_called_with('_mr_')
        bp.print.assert_called()
