#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#
# <bitbar.title>Noti</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>ye11ow</bitbar.author>
# <bitbar.author.github>ye111111ow</bitbar.author.github>
# <bitbar.desc>Show the status of merge requests</bitbar.desc>
# <bitbar.image></bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/ye11ow/noti</bitbar.abouturl>

import sys
import json
from pathlib import Path
from datetime import datetime

# Put your personal configuration here
DEFAULT_CONFIG = {
    # Gitlab related configurations
    'gitlab': {
        # Go to the "User Settings" -> "Access Tokens" page, create a Personal Access Token with "api" Scopes
        'token': '',

        # Go to the home page of the repo, you will find the Project ID under the name of the repo (in grey).
        'project_id': [],

        # The host of the gitlab server. e.g. https://gitlab.example.com
        'host': '',
    },

    # Github related configurations
    'github': {
        'token': '',
        'repo': ['']
    }
}

class NotiError(Exception):
    def __init__(self, title, message):
        self.title = title
        self.message = message

class Gitlab:
    def __init__(self, config):
        try:
            import gitlab
        except:
            raise NotiError('Missing dependencies', 'You need to install python-gitlab | href=https://python-gitlab.readthedocs.io/en/stable/install.html')

        self._config = config.get('gitlab', {})

        host = self._config.get('host', '')
        token = self._config.get('token', '')
        if len(host) + len(token) == 0:
            raise NotiError('Wrong Gitlab configuration', 'Please make sure you have the right host and token')
    
        self._gl = gitlab.Gitlab(host, private_token=token)

    def get_mrs(self):
        mrs = []

        for pid in self._config.get('project_id'):
            project = self._gl.projects.get(pid)
            for list_mr in project.mergerequests.list(state='opened'):
                mr = project.mergerequests.get(list_mr.get_id())
                mrs.append(GitlabMR(project, mr))

        return mrs

class GitlabMR:
    def __init__(self, project, mr):
        self._project = project
        self._mr = mr

    @property
    def ci_failed(self):
        return self.ci_status == 'failed'

    @property
    def ci_status(self):
        pipeline = self._mr.attributes.get('pipeline')
        if pipeline:
            return pipeline.get('status', None)

    @property
    def failed_pipeline_jobs(self):
        if not hasattr(self, '_failed_pipeline_jobs'):
            self._failed_pipeline_jobs = []
            if self._mr.attributes.get('pipeline'):
                jobs = self._project.pipelines.get(self._mr.attributes.get('pipeline')['id'], lazy=True).jobs.list(scope='failed')
                self._failed_pipeline_jobs = list(map(lambda x: PipelineJob(x), jobs))

        return self._failed_pipeline_jobs

    @property
    def approved(self):
        if not hasattr(self, '_approved'):
            self._approved = self._mr.approvals.get().attributes.get('approved')

        return self._approved

    @property
    def url(self):
        return self._mr.attributes.get('web_url')

    @property
    def branch(self):
        return self._mr.attributes.get('source_branch')

    @property
    def has_review(self):
        return self._mr.attributes.get('user_notes_count', -1) > 0

    # return unresolved, non-system notes only
    @property
    def reviews(self):

        def note_filter(note):
            if note.attributes.get('system'):
                return False

            if note.attributes.get('resolvable') and note.attributes.get('resolved'):
                return False

            return True

        if not hasattr(self, '_reviews'):
            reviews = self._mr.notes.list()
            reviews = list(filter(lambda x: note_filter(x), reviews))
            self._reviews = list(map(lambda x: GitlabReview(self, x), reviews))

        return self._reviews

class PipelineJob:
    def __init__(self, job):
        self._job = job

    @property
    def name(self):
        return self._job.attributes.get('name')

    @property
    def url(self):
        return self._job.attributes.get('web_url')

class GitlabReview:
    def __init__(self, mr, review):
        self._mr = mr
        self._review = review

    @property
    def author(self):
        return self._review.attributes.get('author')['name']

    @property
    def created_at(self):
        return parser.parse(self._review.attributes.get('created_at')).astimezone(tzlocal())

    @property
    def body(self):
        return self._review.attributes.get('body')

    @property
    def url(self):
        return f"{self._mr.url}#note_{self._review.get_id()}"

class Github:
    def __init__(self, config):
        try:
            from github import Github as GH
        except:
            raise NotiError('Missing dependencies', 'You need to install PyGithub | href=https://pygithub.readthedocs.io/en/latest/introduction.html#download-and-install')

        self._config = config.get('github', {})
        token = self._config.get('token', '')
        if len(token) == 0:
            raise NotiError('Wrong Github configuration', 'Please make sure you have the right token')

        self._gh = GH(token)

    def get_mrs(self):
        mrs = []

        for repo_name in self._config.get('repo'):
            repo = self._gh.get_repo(repo_name)
            pulls = repo.get_pulls(state='open', sort='created', base='master')
            for pr in pulls:
                mrs.append(GithubPR(pr))

        return mrs

class GithubPR:
    def __init__(self, pr):
        self._pr = pr

    @property
    def ci_failed(self):
        return False

    @property
    def ci_status(self):
        return 'success'

    @property
    def failed_pipeline_jobs(self):
        return []

    @property
    def approved(self):
        return self._pr.mergeable

    @property
    def url(self):
        return self._pr.html_url

    @property
    def branch(self):
        return self._pr.head.ref

    @property
    def has_review(self):
        return self._pr.comments > 0

    @property
    def reviews(self):
        if not hasattr(self, '_comments'):
            comments = []
            for comment in self._pr.get_comments():
                comments.append(GithubComment(comment))

            self._comments = comments

        return self._comments

class GithubComment:
    def __init__(self, comment):
        self._comment = comment

    @property
    def author(self):
        return self._comment.user.login

    @property
    def created_at(self):
        return self._comment.created_at.astimezone(tzlocal())

    @property
    def body(self):
        return self._comment.body

    @property
    def url(self):
        return self._comment.html_url

class BitbarPrinter:
    def __init__(self):
        pass

    def print_config(self):
        print('---\n')
        print('Configure noti | bash="vi $HOME/.noticonfig.json"')
    
    def print_error(self, title, extra):
        print(title)
        print('---\n')
        if extra:
            print(extra)
            print('\n')
        bp.print_config()
        exit(1)

    def print_mr(self, mr):
        pipeline_color_map = {
            'success': 'green',
            'failed': 'red',
            'running': 'blue'
        }

        title = ''
        if mr.approved:
            title += ' 👍'
        title += f" | href={mr.url}"

        sub_text = ''

        # pipeline field will be empty if it is cancelled
        if mr.ci_status in pipeline_color_map:
            title += f" color={pipeline_color_map[mr.ci_status]}"
            if mr.ci_status == 'failed':
                sub_text += '--Failed jobs\n'
                for job in mr.failed_pipeline_jobs:
                    sub_text += f"--{job.name} | color=red href={job.url}\n"

        if len(mr.reviews) > 0:
            diff = datetime.now().astimezone(tzlocal()) - mr.reviews[0].created_at

            sub_text += '-----\n'
            sub_text += f"--Discussions ({diff})\n"

            for review in mr.reviews:
                firstname = review.author.split(' ')[0]
                short = review.body.replace('-', '').replace('\n', '').replace('\r', '')
                short = short[:32]
                sub_text += f"--{firstname}: {short} | href={review.url}\n"

        if len(mr.reviews) == 0:
            title = f"{mr.branch} {title}"
        else:
            title = f"{mr.branch} 💬{len(mr.reviews)} {title}"

        print(f"{title}\n\n\n{sub_text}")

    def print_title(self, mrs):
        statistics = {
            'approved': 0,
            'failed': 0,
            'running': 0,
            'comments': 0
        }
        pipeline_icon_map = {
            'failed': '🙃',
            'running': '🏃',
            'comments': '💬',
            'approved': '👍'
        }

        for mr in mrs:
            statistics['comments'] += len(mr.reviews)

            if mr.approved:
                statistics['approved'] += 1

            if mr.ci_status in statistics:
                statistics[mr.ci_status] += 1

        title = ''
        for key in statistics:
            if statistics[key] > 0:
                title += pipeline_icon_map[key] + str(statistics[key])

        if len(title) == 0:
            title = f"{len(mrs)} MRs"

        print(title)
        print('---\n')

bp = BitbarPrinter()

try:
    from dateutil import parser
    from dateutil.tz import tzlocal
except:
    bp.print_error('Missing dependencies', 'You need to install python-dateutil | href=https://dateutil.readthedocs.io/en/stable/#installation')

if __name__== "__main__":
    config_path = Path(Path.home(), ".noticonfig.json")
    user_config = {}
    if not config_path.exists():
        config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=4))

    user_config = json.loads(config_path.read_text())
    config = {**DEFAULT_CONFIG, **user_config}

    vcs = None
    try:
        if 'gitlab' in user_config:
            vcs = Gitlab(config)
        elif 'github' in user_config:
            vcs = Github(config)
    except NotiError as err:
        bp.print_error(err.title, err.message)
        
    try:
        mrs = vcs.get_mrs()
    except:
        bp.print_error("failed to connect to the server", None)
        
    bp.print_title(mrs)
    for mr in mrs:
        bp.print_mr(mr)
    bp.print_config()