from unittest.mock import MagicMock
import pytest

from noti import GitlabMR

class DummyNote:
    def __init__(self, system, resolvable, resolved):
        self.attributes = {
            'system': system,
            'resolvable': resolvable,
            'resolved': resolved
        }

class TestGitlabMR:

    @pytest.fixture(autouse=True)
    def mr(self):
        return GitlabMR(MagicMock(), MagicMock())

    def test_ci_failed(self, mr):
        mr._mr.attributes.get.return_value = {
            'status': 'failed'
        }

        assert mr.ci_failed
        mr._mr.attributes.get.assert_called_with('pipeline')


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
        notes = [DummyNote(True, False, False), DummyNote(False, True, True), DummyNote(False, False, False), DummyNote(False, True, False)]
        mr._mr.notes.list.return_value = notes

        assert len(mr.reviews) == 2

    def test_reviews_fail(self, mr):
        assert 1 == 2