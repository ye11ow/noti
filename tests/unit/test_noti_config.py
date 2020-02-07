import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from noti import NotiConfig
from noti import NotiError

class TestNotiConfig:

    @patch('noti.Gitlab')
    def test_init_vcs_gitlab(self, gitlab):
        fp = tempfile.NamedTemporaryFile('w')
        fp.write('''
        {
            "gitlab": {}
        }
        ''')
        fp.flush()
        conf = NotiConfig(Path(fp.name))
        vcs = conf.init_vcs()
        fp.close()

        assert vcs == gitlab.return_value 

    @patch('noti.Github')
    def test_init_vcs_github(self, github):
        fp = tempfile.NamedTemporaryFile('w')
        fp.write('''
        {
            "github": {}
        }
        ''')
        fp.flush()
        conf = NotiConfig(Path(fp.name))
        vcs = conf.init_vcs()
        fp.close()

        assert vcs == github.return_value 

    def test_init_vcs_none(self):
        fp = tempfile.NamedTemporaryFile('w')
        fp.write('''
        {
            "random": {}
        }
        ''')
        fp.flush()
        conf = NotiConfig(Path(fp.name))

        with pytest.raises(NotiError):
            vcs = conf.init_vcs()

        fp.close()