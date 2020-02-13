from unittest.mock import MagicMock
import pytest

from noti import GitlabMR
from fixtures import gitlab as mock

class TestGitlabMR:

    @pytest.fixture
    def mr(self):
        return GitlabMR(MagicMock(), MagicMock())

    def test_title(self, mr):
        mr._mr.attributes.get.return_value = 'mytitle'

        assert mr.title == 'mytitle'
        mr._mr.attributes.get.assert_called_with('title')

    def test_ci_status(self, mr):
        pipeline = MagicMock()
        mr._mr.attributes.get.return_value = pipeline

        pipeline.get.return_value = 'mystatus'

        assert mr.ci_status == 'mystatus'
        mr._mr.attributes.get.assert_called_with('pipeline')
        pipeline.get.assert_called_with('status', None)
    

    def test_failed_pipeline_jobs(self, mr):
        mr._mr.attributes.get.return_value = {
            'id': 123
        }
        mr._project.pipelines.get.return_value.jobs.list.return_value = [1,2,3,4,5]
        
        assert len(mr.failed_pipeline_jobs) == 5
        mr._mr.attributes.get.assert_called_with('pipeline')
        mr._project.pipelines.get.return_value.jobs.list.assert_called_with(scope='failed')

    def test_approved(self, mr):
        mr._mr.approvals.get.return_value.attributes.get.return_value = True

        assert mr.approved
        mr._mr.approvals.get.return_value.attributes.get.assert_called_with('approved')
        
    def test_url(self, mr):
        mr._mr.attributes.get.return_value = 'myurl'

        assert mr.url == 'myurl'
        mr._mr.attributes.get.assert_called_with('web_url')
    
    def test_branch(self, mr):
        mr._mr.attributes.get.return_value = 'mybranch'

        assert mr.branch == 'mybranch'
        mr._mr.attributes.get.assert_called_with('source_branch')

    def test_has_review(self, mr):
        mr._mr.attributes.get.return_value = 5

        assert mr.has_review
        mr._mr.attributes.get.assert_called_with('user_notes_count', -1)
            
    def test_reviews(self, mr):
        notes = [
            mock.DummyReview(system=True, resolvable=False, resolved=False), 
            mock.DummyReview(system=False, resolvable=True, resolved=True), 
            mock.DummyReview(system=False, resolvable=False, resolved=False), 
            mock.DummyReview(system=False, resolvable=True, resolved=False)
        ]
        mr._mr.notes.list.return_value = notes

        assert len(mr.reviews) == 2