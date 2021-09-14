from unittest.mock import MagicMock

from dateutil import parser

class DummyComment:

    def __init__(self):
        self._user = MagicMock()
        self._user.login = '_author_'
    
    @property
    def user(self):
        return self._user

    @property
    def created_at(self):
        return parser.parse('2020-02-02T20:20:20Z')

    @property
    def body(self):
        return '_body_'
    
    @property
    def html_url(self):
        return '_url_'

class DummyPR:

    def __init__(self, comments=[], mergeable_state='clean'):
        self._head = MagicMock()
        self._head.ref = '_branch_'
        self._head.sha = '_sha_'
        self._comments = comments
        self._mergeable_state = mergeable_state

    def get_comments(self):
        return self._comments

    @property
    def title(self):
        return '_title_'

    @property
    def html_url(self):
        return '_url_'

    @property
    def head(self):
        return self._head
    
    @property
    def mergeable(self):
        return True

    @property
    def mergeable_state(self):
        return self._mergeable_state

class DummyBuild:

    def __init__(self, state='success'):
        self._state = state
    
    @property
    def state(self):
        return self._state

    @property
    def context(self):
        return '_name_'

    @property
    def target_url(self):
        return '_url_'