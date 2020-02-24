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