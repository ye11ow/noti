import tempfile
from pathlib import Path
import pytest

from noti import NotiConfig
from noti import NotiError

class TestNotiConfig:

    def test_user_config(self):
        fp = tempfile.NamedTemporaryFile('w')
        fp.write('''
        {
            "gitlab": {}
        }
        ''')
        fp.flush()
        conf = NotiConfig(Path(fp.name))
        fp.close()

        assert 'gitlab' in conf.user_config
        assert 'global' not in conf.user_config

    def test_get_config(self):
        fp = tempfile.NamedTemporaryFile('w')
        fp.write('''
        {
            "github": {
                "hello": "world"
            }
        }
        ''')
        fp.flush()
        conf = NotiConfig(Path(fp.name))
        fp.close()

        config = conf.get_config('github')

        assert config.get('mr_limit') == 5
        assert config.get('hello') == 'world'
