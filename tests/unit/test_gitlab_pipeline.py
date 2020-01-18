from unittest.mock import MagicMock

from noti import PipelineJob

class TestGitlabPipeline:

    def test_name(self):
        mock_job = MagicMock()
        mock_job.attributes.get.return_value = 'myjob'

        review = PipelineJob(mock_job)

        assert review.name == 'myjob'
        mock_job.attributes.get.assert_called_with('name')

    def test_url(self):
        mock_job = MagicMock()
        mock_job.attributes.get.return_value = 'myurl'

        review = PipelineJob(mock_job)

        assert review.url == 'myurl'
        mock_job.attributes.get.assert_called_with('web_url')