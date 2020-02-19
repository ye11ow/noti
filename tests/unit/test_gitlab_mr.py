from unittest.mock import MagicMock
import pytest

from noti import GitlabMR
from fixtures import gitlab as mock

class TestGitlabMR:

    @pytest.fixture
    def default_mr(self):
        return GitlabMR(MagicMock(), mock.DummyMR())

    def test_title(self, default_mr):
        assert default_mr.title == '_title_'

    def test_ci_status(self, default_mr):
        assert default_mr.ci_status == 'success'

    def test_failed_pipeline_jobs(self):
        mock_project = MagicMock()
        mock_project.pipelines.get.return_value.jobs.list.return_value = [1,2,3,4,5]
        mr = GitlabMR(mock_project, mock.DummyMR())
        
        assert len(mr.failed_pipeline_jobs) == 5
        mock_project.pipelines.get.return_value.jobs.list.assert_called_with(scope='failed')

    def test_approved(self, default_mr):
        assert default_mr.approved
        
    def test_url(self, default_mr):
        assert default_mr.url == '_url_'
    
    def test_branch(self, default_mr):
        assert default_mr.branch == '_branch_'
            
    def test_reviews(self):
        notes = [
            mock.DummyReview(system=True, resolvable=False, resolved=False), 
            mock.DummyReview(system=False, resolvable=True, resolved=True), 
            mock.DummyReview(system=False, resolvable=False, resolved=False), 
            mock.DummyReview(system=False, resolvable=True, resolved=False)
        ]

        mr = GitlabMR(MagicMock(), mock.DummyMR(reviews=notes))

        assert len(mr.reviews) == 2