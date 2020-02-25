import pytest

from noti import VCS

class DummyVCS(VCS):

    def __init__(self, config):
        super().__init__('_name_', config, '_host_')
    

class TestVCS:

    @pytest.fixture
    def vcs(self):
        return DummyVCS({
            '_name_': {
                'config': '_config_',
                'duplicate_config': 'dummy_config'
            },
            'global': {
                'duplicate_config': 'global_config',
                'global_config': '_global_config_'
            }
        })
    
    def test_get_config(self, vcs):
        assert vcs.get_config('config') == '_config_'
        assert vcs.get_config('global_config') == '_global_config_'

    def test_get_config_override(self, vcs):
        assert vcs.get_config('duplicate_config') == 'dummy_config'

    def test_get_config_default_value(self, vcs):
        assert vcs.get_config('config', 'wrong') == '_config_'
        assert vcs.get_config('no_config', 'right') == 'right'