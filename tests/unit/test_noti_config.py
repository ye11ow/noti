import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from noti import NotiConfig

def create_tempfile(content):
    fp = tempfile.NamedTemporaryFile('w')
    fp.write(content)
    fp.flush()
    conf = NotiConfig(Path(fp.name))
    fp.close()

    return conf

class TestNotiConfig:

    @patch('noti.Path.home')
    def test_init_config(self, home):
        home.return_value = tempfile.tempdir
        path = Path(home.return_value, ".noticonfig.json")

        assert not path.exists()
        
        conf = NotiConfig()
        content = path.read_text()
        path.unlink()
        default_config = json.loads(content)

        assert default_config == conf.DEFAULT_CONFIG
        assert not path.exists()



    def test_user_config(self):
        conf = create_tempfile('''
        {
            "gitlab": {}
        }
        ''')

        assert 'gitlab' in conf.user_config
        assert 'global' not in conf.user_config

    def test_get_config(self):
        conf = create_tempfile('''
        {
            "github": {
                "hello": "world"
            }
        }
        ''')

        config = conf.get_config('github')

        assert config.get('mr_limit') == 10
        assert config.get('hello') == 'world'

    def test_emoji_config(self):
        conf = create_tempfile('''
        {
            "emoji": {
                "running": "_running_"
            }
        }
        ''')

        emoji = conf.emoji_config
        assert emoji.get('running') == '_running_'
        assert emoji.get('failed') == NotiConfig.DEFAULT_CONFIG.get('emoji').get('failed')