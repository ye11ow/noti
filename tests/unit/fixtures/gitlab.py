from unittest.mock import MagicMock

# mock Gitlab Review response
class DummyReview:
    def __init__(self, id='_id_', system=False, resolvable=True, resolved=False, author='_author_', created_at='2020-02-02T20:20:20Z', body='_body_'):
        self._id = id
        self.attributes = {
            'system': system,
            'resolvable': resolvable,
            'resolved': resolved,
            'author': {
                'name': author
            },
            'created_at': created_at,
            'body': body
        }

    def get_id(self):
        return self._id

# mock Gitlab MR response
class DummyMR:
    def __init__(self, title='_title_', status='success', pipeline_id='_pid_', url='_url_', branch='_branch_', reviews=[], approved=True):
        self.attributes = {
            'title': title,
            'pipeline': {
                'status': status,
                'id': pipeline_id
            },
            'web_url': url,
            'source_branch': branch
        }
        self.notes = MagicMock()
        self.notes.list.return_value = reviews
        self.approvals = MagicMock()
        self.approvals.get.return_value.attributes.get.return_value = approved


