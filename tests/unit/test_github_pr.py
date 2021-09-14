from unittest.mock import MagicMock
import pytest

from noti import GithubPR
from fixtures import github as mock

class TestGithubPR:

    @pytest.fixture
    def default_pr(self):
        return GithubPR(MagicMock(), mock.DummyPR())

    def test_title(self, default_pr):
        assert default_pr.title == '_title_'
    
    def test_ci_status(self, default_pr):
        default_pr._repo.get_commit.return_value.get_combined_status.return_value.statuses = [1]
        default_pr._repo.get_commit.return_value.get_combined_status.return_value.state = 'success'
        assert default_pr.ci_status == 'success'
        default_pr._repo.get_commit.assert_called_with('_sha_')
        default_pr._repo.get_commit.return_value.get_combined_status.assert_called_once()
    
    def test_ci_status_no_statuses(self, default_pr):
        default_pr._repo.get_commit.return_value.get_combined_status.return_value.state = 'pending'
        assert default_pr.ci_status == ''
        default_pr._repo.get_commit.assert_called_with('_sha_')
        default_pr._repo.get_commit.return_value.get_combined_status.assert_called_once()

    def test_failed_pipeline_jobs(self, default_pr):
        default_pr._status = MagicMock()
        default_pr._status.statuses = [
            mock.DummyBuild('failure'),
            mock.DummyBuild(),
            mock.DummyBuild('failure'),
            mock.DummyBuild(),
            mock.DummyBuild('failure')
        ]

        assert len(default_pr.failed_pipeline_jobs) == 3

    def test_approved(self, default_pr):
        assert default_pr.approved

    def test_not_approved(self):
        pr = GithubPR(MagicMock(), mock.DummyPR(mergeable_state='blocked'))
        assert not pr.approved

    def test_url(self, default_pr):
        assert default_pr.url == '_url_'
    
    def test_branch(self, default_pr):
        assert default_pr.branch == '_branch_'

    def test_reviews(self):
        comments = [
            mock.DummyComment(),
            mock.DummyComment(),
            mock.DummyComment()
        ]
        pr = GithubPR(MagicMock(), mock.DummyPR(comments=comments))

        assert len(pr.reviews) == 3