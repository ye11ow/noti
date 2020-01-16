import sys

class TestNoti:

    def test_import(self):
        # This test tries to make sure neither github nor gitlab would be loaded
        # by default. We only want to load those modules when they are configured
        # by the user.
        import noti

        assert not 'github' in sys.modules
        assert not 'gitlab' in sys.modules
        assert 'dateutil' in sys.modules