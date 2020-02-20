from unittest.mock import MagicMock
import pytest

from noti import PipelineJob
from fixtures import gitlab as mock

class TestGitlabPipeline:

    @pytest.fixture(autouse=True)
    def job(self):
        return PipelineJob(mock.DummyJob())

    def test_name(self, job):
        assert job.name == '_name_'

    def test_url(self, job):
        assert job.url == '_url_'
