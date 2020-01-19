from unittest.mock import MagicMock
import pytest

from noti import PipelineJob

class TestGitlabPipeline:

    @pytest.fixture(autouse=True)
    def job(self):
        return PipelineJob(MagicMock())

    def test_name(self, job):
        job._job.attributes.get.return_value = 'myjob'

        assert job.name == 'myjob'
        job._job.attributes.get.assert_called_with('name')

    def test_url(self, job):
        job._job.attributes.get.return_value = 'myurl'

        assert job.url == 'myurl'
        job._job.attributes.get.assert_called_with('web_url')