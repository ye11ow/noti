import tempfile
from pathlib import Path
from unittest.mock import patch

from noti import NotiConfig

class TestNotiConfig:

    @patch('noti.Gitlab')
    def test_init_vcs_gitlab(self, gitlab):
        fp = tempfile.NamedTemporaryFile('w')
        fp.write('''
        {
            "gitlab": {
            }
        }
        ''')
        fp.flush()
        conf = NotiConfig(Path(fp.name))
        vcs = conf.init_vcs()
        fp.close()

        assert vcs

    @patch('noti.Github')
    def test_init_vcs_github(self, github):
        fp = tempfile.NamedTemporaryFile('w')
        fp.write('''
        {
            "github": {
            }
        }
        ''')
        fp.flush()
        conf = NotiConfig(Path(fp.name))
        vcs = conf.init_vcs()
        fp.close()

        assert vcs


