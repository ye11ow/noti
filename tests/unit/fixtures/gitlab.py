# mock Gitlab Review response
class DummyReview:
    def __init__(self, id="_id_", system=False, resolvable=True, resolved=False, author="_author_", created_at="2020-02-02T20:20:20Z", body="_body_"):
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
    def __init__(self, url="_url_"):
        self._url = url

    @property
    def url(self):
        return self._url