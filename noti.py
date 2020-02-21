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

class VCS:

    def __init__(self, config):
        self._config = config.get(self.name, {})
        self._global_config = config.get('global', {})

    def get_config(self, item, default_value=None):
        if item in self._config:
            return self._config.get(item)
        if item in self._global_config:
            return self._global_config.get(item)
        
        return default_value

    @property
    def name(self):
        raise NotImplementedError

    def get_mrs(self):
        raise NotImplementedError

class Review:

    def __init__(self, author, created_at, body, url):
        self._author = author
        self._created_at = created_at
        self._body = body
        self._url = url

    @property
    def author(self):
        return self._author

    @property
    def created_at(self):
        return self._created_at

    @property
    def body(self):
        return self._body

    @property
    def url(self):
        return self._url

class MR:

    def __init__(self, title, url, branch, ci_status=None):
        self._title = title
        self._ci_status = ci_status
        self._url = url
        self._branch = branch

    @property
    def title(self):
        return self._title
    
    @property
    def ci_status(self):
        return self._ci_status

    @property
    def url(self):
        return self._url

    @property
    def branch(self):
        return self._branch

class CIJob:

    def __init__(self, name, url):
        self._name = name
        self._url = url
    
    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

class NotiConfig:

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
            # Go to Github "Settings" -> "Developer settings" -> "Personal access tokens" and "Generate new token" with "repo" scopes
            'token': '',

            # The name of the repo, e.g. "ye11ow/noti"
            'repo': ['']
        },

        # Shared configurations
        'global': {
            # Max number of MRs that will be shown on the list
            'mr_limit': 5
        }
    }

    def __init__(self, path=None):
        if not path:
            path = Path(Path.home(), ".noticonfig.json")
        self.conf_path = path

        if not self.conf_path.exists():
            self.conf_path.write_text(json.dumps(self.DEFAULT_CONFIG, indent=4))

    def init_vcs(self):
        vcs = []
        user_config = json.loads(self.conf_path.read_text())
        self.config = {**self.DEFAULT_CONFIG, **user_config}

        if 'gitlab' in user_config:
            vcs.append(Gitlab(self.config))
        if 'github' in user_config:
            vcs.append(Github(self.config))
        
        return vcs

class NotiError(Exception):
    def __init__(self, title, message):
        self.title = title
        self.message = message

class Gitlab(VCS):
    def __init__(self, config):
        super().__init__(config)
        
        try:
            import gitlab
        except:
            raise NotiError('Missing dependencies', 'You need to install python-gitlab | href=https://python-gitlab.readthedocs.io/en/stable/install.html')

        host = self.get_config('host', '')
        token = self.get_config('token', '')
        if len(host) + len(token) == 0:
            raise NotiError('Wrong Gitlab configuration', 'Please make sure you have the right host and token')
    
        self._gl = gitlab.Gitlab(host, private_token=token)

    @property
    def name(self):
        return 'gitlab'

    def get_mrs(self):
        mrs = {}

        for pid in self.get_config('project_id', []):
            project = self._gl.projects.get(pid)
            name = project.attributes.get('name')
            mrs[name] = []
            for list_mr in project.mergerequests.list(state='opened', per_page=self.get_config('mr_limit')):
                mr = project.mergerequests.get(list_mr.get_id())
                mrs[name].append(GitlabMR(project, mr))

        return mrs

class GitlabMR(MR):
    def __init__(self, project, mr):
        self._project = project
        self._mr = mr

        pipeline = mr.attributes.get('pipeline')
        ci_status = pipeline.get('status', None) if pipeline else None
        super().__init__(
            title=mr.attributes.get('title'),
            ci_status=ci_status,
            url=mr.attributes.get('web_url'),
            branch=mr.attributes.get('source_branch')
        )

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

class PipelineJob(CIJob):
    
    def __init__(self, job):
        super().__init__(
            name=job.attributes.get('name'),
            url=job.attributes.get('web_url')
        )

class GitlabReview(Review):

    def __init__(self, mr, review):
        super().__init__(
            author=review.attributes.get('author')['name'],
            created_at=parser.parse(review.attributes.get('created_at')).astimezone(tzlocal()),
            body=review.attributes.get('body'),
            url=f"{mr.url}#note_{review.get_id()}"
        )

class Github(VCS):
    def __init__(self, config):
        super().__init__(config)

        try:
            import github
        except:
            raise NotiError('Missing dependencies', 'You need to install PyGithub | href=https://pygithub.readthedocs.io/en/latest/introduction.html#download-and-install')

        token = self.get_config('token', '')
        if len(token) == 0:
            raise NotiError('Wrong Github configuration', 'Please make sure you have the right token')

        self._gh = github.Github(token)

    @property
    def name(self):
        return 'github'

    def get_mrs(self):
        mrs = {}

        for repo_name in self.get_config('repo', []):
            mrs[repo_name] = []
            repo = self._gh.get_repo(repo_name)
            pulls = repo.get_pulls(state='open', sort='created', base='master')
            for pr in pulls:
                mrs[repo_name].append(GithubPR(repo, pr))
                
                # Github SDK doesn't support per_page parameter
                if len(mrs[repo_name]) >= self.get_config('mr_limit'):
                    break

        return mrs

class GithubPR(MR):
    def __init__(self, repo, pr):
        self._repo = repo
        self._pr = pr

        super().__init__(
            title=pr.title,
            url=pr.html_url,
            branch=pr.head.ref
        )

    @property
    def ci_status(self):
        if not hasattr(self, '_status'):
            sha = self._pr.head.sha
            self._status = self._repo.get_commit(sha).get_combined_status()
        
        state = self._status.state
        if state == 'pending':
            return 'running'
        elif state == 'failure':
            return 'failed'
        else:
            return state

    @property
    def failed_pipeline_jobs(self):
        if not hasattr(self, '_failed_pipeline_jobs'):
            statuses = list(filter(lambda x: x.state == 'failure', self._status.statuses))
            self._failed_pipeline_jobs = list(map(lambda x: TravisBuild(x), statuses))

        return self._failed_pipeline_jobs

    @property
    def approved(self):
        return self._pr.mergeable

    @property
    def reviews(self):
        if not hasattr(self, '_comments'):
            comments = []
            for comment in self._pr.get_comments():
                comments.append(GithubComment(comment))

            self._comments = comments

        return self._comments

class TravisBuild(CIJob):

    def __init__(self, build):
        super().__init__(
            name=build.context,
            url=build.target_url
        )

class GithubComment(Review):
    
    def __init__(self, comment):
        super().__init__(
            author=comment.user.login,
            created_at=comment.created_at.replace(tzinfo=tzutc()).astimezone(tzlocal()),
            body=comment.body,
            url=comment.html_url
        )

class BitbarPrinter:
    def __init__(self):
        self._title = ""
        self._items = []
        self._configs = ['Configure noti | bash="vi $HOME/.noticonfig.json"']

    def title(self, title):
        self._title = title    
    
    def add(self, item):
        self._items.append(item)

    def clear(self):
        self.title('')
        self._items = []

    def print(self):
        print(self._title)

        if len(self._items) > 0:
            print('---')
            for item in self._items:
                print(item)
            
        if len(self._configs) > 0:
            print('---')
            for config in self._configs:
                print(config)

    # print_error will override title and body with error messages.
    def print_error(self, title, extra):
        self.clear()

        self.title(title)
        if extra:
            self.add(extra)

        self.print()
        exit(1)

    def generate_mr(self, mr):
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
            sub_text += '-----\n'
            sub_text += f"--Discussions ({self.time_diff(mr.reviews[0].created_at)})\n"

            for review in mr.reviews:
                firstname = review.author.split(' ')[0]
                short = review.body.replace('-', '').replace('\n', '').replace('\r', '')
                short = short[:32]
                sub_text += f"--{firstname}: {short} | href={review.url}\n"

        if len(mr.reviews) == 0:
            title = f"{mr.branch} {title}"
        else:
            title = f"{mr.branch} 💬{len(mr.reviews)} {title}"

        self.add(f"{title}\n\n\n{sub_text}")
        self.add(f"{mr.title} | alternate=true")

    def generate_title(self, mrs):
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

        for key, value in mrs.items():
            for mr in value:
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
            title = '😃'

        self.title(title)

    def time_diff(self, before):
        diff = (datetime.now().astimezone(tzlocal()) - before).seconds

        hours = int(diff/3600)
        hours_text = ''
        if hours > 0:
            hours_text = f"{hours} hours "
        minutes = int(diff%3600/60)

        return f"{hours_text}{minutes} minutes ago"

bp = BitbarPrinter()

try:
    from dateutil import parser
    from dateutil.tz import tzlocal
    from dateutil.tz import tzutc
    from requests.exceptions import ConnectionError
except:
    bp.print_error('Missing dependencies', 'You need to install python-dateutil | href=https://dateutil.readthedocs.io/en/stable/#installation')

if __name__== "__main__":
    conf = NotiConfig()
    vcs = conf.init_vcs()

    if len(vcs) == 0:
        bp.print_error('Wrong configuration', 'You have to configure either gitlab or github')        

    mrs = {}
    try:
        for v in vcs:
            mrs.update(v.get_mrs())   
    except ConnectionError:
        bp.print_error("failed to connect to the server", None)

    bp.generate_title(mrs)
    for repo_name, repo_mrs in mrs.items():
        if len(repo_mrs) == 0:
            continue

        bp.add(repo_name)
        for mr in repo_mrs:
            bp.generate_mr(mr)

    bp.print()
