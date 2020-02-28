from unittest.mock import MagicMock
from unittest.mock import patch
from requests.exceptions import ConnectionError
import pytest

from noti import main

class TestNoti:

    @pytest.fixture
    def bp(self):
        return MagicMock()

    def test_no_vcs(self, bp):
        main([], bp)

        bp.fatal.assert_called

    def test_no_connection(self, bp):
        vcs = MagicMock()
        vcs.name = '_name_'
        vcs.get_mrs.side_effect = ConnectionError()

        main([vcs], bp)

        bp.add_error.assert_called_with('_name_: failed to connect to the server')

    def test_happy_path(self, bp):
        vcs = MagicMock()
        mrs = {
            '_repo_': [
                '_mr_',
                '_mr_'
            ]
        }
        vcs.get_mrs.return_value = mrs
        
        main([vcs], bp)

        bp.generate_title.assert_called_with(mrs) 
        bp.add.assert_called_with('_repo_')
        bp.generate_mr.assert_called_with('_mr_')
        bp.print.assert_called()
