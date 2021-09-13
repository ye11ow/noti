import pytest

from noti import VCS

class DummyVCS(VCS):

    name = '_name_'

    def __init__(self, config):
        super().__init__(config, '_host_')

class DummyVCSNoname(VCS):
    
    def __init__(self, config):
        super().__init__(config, '_host_')
    

class TestVCS:

    @pytest.fixture
    def vcs(self):
        return DummyVCS({
            'config': '_config_',
            'global_config': '_global_config_',
            'token': '_token_'
        })
    
    def test_get_config(self, vcs):
        assert vcs.get_config('config') == '_config_'
        assert vcs.get_config('global_config') == '_global_config_'

    def test_get_config_default_value(self, vcs):
        assert vcs.get_config('config', 'wrong') == '_config_'
        assert vcs.get_config('no_config', 'right') == 'right'
    
    def test_name(self, vcs):
        assert vcs.name == '_name_'

    def test_token(self, vcs):
        assert vcs.token == '_token_'

    def test_no_name_vcs(self):
        vcs = DummyVCSNoname({})
        with pytest.raises(NotImplementedError):
            assert vcs.name