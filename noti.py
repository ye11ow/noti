#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#
# <xbar.title>Noti</xbar.title>
# <xbar.version>v0.5.1</xbar.version>
# <xbar.author>ye11ow</xbar.author>
# <xbar.author.github>ye11ow</xbar.author.github>
# <xbar.desc>Show the status of the merge requests</xbar.desc>
# <xbar.image>https://raw.githubusercontent.com/ye11ow/noti/main/docs/images/Bitbar.png</xbar.image>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/ye11ow/noti</xbar.abouturl>

import json
from pathlib import Path
from datetime import datetime

class VCS:

    def __init__(self, config, default_host):
        self._config = config
        self._default_host = default_host

    def get_config(self, item, default_value=None):
        return self._config.get(item, default_value)

    @property
    def name(cls):
        raise NotImplementedError

    @property
    def token(self):
        token = self.get_config('token', '')
        if len(token) == 0:
            raise NotiError(self.name, 'Wrong configuration: Please make sure you have the right token')

        return token

    @property
    def host(self):
        host = self.get_config('host', '')
        if len(host) == 0:
            host = self._default_host
        
        return host

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

            # [Optional] The host of the gitlab server. Leave it empty to use the public Gitlab server.
            'host': '',

            # [Optional] Filters
            'filters': {

                # [Optional] Filter by the usernames. The username here is the @ ID
                'usernames': []
            }
        },

        # Github related configurations
        'github': {
            # Go to Github "Settings" -> "Developer settings" -> "Personal access tokens" and "Generate new token" with "repo" scopes
            'token': '',

            # The name of the repo, e.g. "ye11ow/noti"
            'repo': [''],

            # [Optional] The host of the github server. Leave it empty to use the public Github server.
            'host': '',

            # [Optional] Filters
            "filters": {
                # [Optional] Filter by the usernames. The username here is the ID. e.g. https://github.com/ye11ow ye11ow is the username.
                "usernames": []
            }
        },

        # Shared configurations
        'global': {
            # Max number of MRs that will be shown on the list
            'mr_limit': 10,
        },

        'emoji': {
            'good_day': '😃',
            'approved': '👍',
            'running': '🏃',
            'failed': '🙃',
            'comments': '💬'
        }
    }

    def __init__(self, path=None):
        if not path:
            path = Path(Path.home(), ".noticonfig.json")
        self.conf_path = path

        if not self.conf_path.exists():
            self.conf_path.write_text(json.dumps(self.DEFAULT_CONFIG, indent=4))

        self._user_config = json.loads(self.conf_path.read_text())
        self._shared_config = self.DEFAULT_CONFIG.get('global')

    @property
    def user_config(self):
        return self._user_config

    def get_config(self, vcs):
        return {**self._shared_config, **self.user_config.get(vcs)}
    
    @property
    def emoji_config(self):
        return {**self.DEFAULT_CONFIG.get('emoji'), **self.user_config.get('emoji', {})}

class NotiError(Exception):
    def __init__(self, vcs, message, help_link=None):
        self.vcs = vcs
        self.message = message
        self.help_link = help_link

class Gitlab(VCS):
    
    name = 'Gitlab'

    def __init__(self, config):
        super().__init__(config, 'https://gitlab.com')
        
        try:
            import gitlab
        except:
            raise NotiError(self.name, 'Missing dependencies: You need to install python-gitlab', 'https://python-gitlab.readthedocs.io/en/stable/install.html')

        self._gl = gitlab.Gitlab(self.host, private_token=self.token)

    def get_mrs(self):
        mrs = {}

        for pid in self.get_config('project_id', []):
            project = self._gl.projects.get(pid)
            name = project.attributes.get('name')
            mrs[name] = []
            filters = self.get_config('filters', {})
            if 'usernames' in filters and len(filters['usernames']) > 0:
                mr_limit = self.get_config('mr_limit')
                for list_mr in project.mergerequests.list(state='opened', per_page=100):
                    if mr_limit == 0:
                        break
                    if list_mr.author.get('username', None) in filters['usernames']:
                        mr = project.mergerequests.get(list_mr.get_id())
                        mrs[name].append(GitlabMR(project, mr))
                        mr_limit -= 1
            else:
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
                self._failed_pipeline_jobs = [PipelineJob(x) for x in jobs]

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
            self._reviews = [GitlabReview(self, x) for x in reviews]

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

    name = 'Github'

    def __init__(self, config):
        super().__init__(config, 'https://api.github.com')

        try:
            import github
        except:
            raise NotiError(self.name, 'Missing dependencies: You need to install PyGithub', 'https://pygithub.readthedocs.io/en/latest/introduction.html#download-and-install')

        self._gh = github.Github(self.token, base_url=self.host, per_page=self.get_config('mr_limit'))

    def get_mrs(self):
        mrs = {}

        filters = self.get_config('filters', {})

        # If any filter is set, we need to get all the PRs and filter them locally
        if 'usernames' in filters and len(filters['usernames']) > 0:
            self._gh.per_page = 100

        for repo_name in self.get_config('repo', []):
            mrs[repo_name] = []
            repo = self._gh.get_repo(repo_name)
            mr_limit = self.get_config('mr_limit')

            # Here we only get the first page.
            # Github supports page size up to 100 and it is more than enough for us
            pulls = repo.get_pulls(state='open', sort='created', base='main').get_page(0)
            for pr in pulls:
                if 'usernames' in filters and len(filters['usernames']) > 0:
                    if mr_limit == 0:
                        break
                    if pr.user.login in filters['usernames']:
                        mrs[repo_name].append(GithubPR(repo, pr))
                        mr_limit -= 1
                else:
                    # The mr_limit is handled by the Github side
                    mrs[repo_name].append(GithubPR(repo, pr))

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
        
        # The `state` will be pending even if there is no `statuses`
        if len(self._status.statuses) == 0:
            return ''

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
            self._failed_pipeline_jobs = [TravisBuild(x) for x in statuses]

        return self._failed_pipeline_jobs

    # As long as the state is not BLOCKED, we should consider the MR is approved.
    @property
    def approved(self):
        return self._pr.mergeable and self._pr.mergeable_state != 'blocked'

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

# Embedded version of Xbar SDK
class XbarItem:

    def __init__(self, title="", level=1):
        self._title = title
        self._level = level
        self._children = []
        self._param = {}
    
    def __str__(self):
        # It's OK to have `_level < 2` here.
        value = "--" * (self._level - 2) + self._title

        params = []
        for key in sorted(self._param.keys()):
            params.append(f"{key}={self._param[key]}")
                
        if len(params) > 0:
            value += " | " 
            value += " ".join(params)

        if len(self._children) > 0:
            value += "\n"

            # This is the title item
            if (self._level == 1):
                value += "---\n"

            for child in self._children:
                if isinstance(child, XbarSeperator):
                    value += "-" * (self._level * 2 + 1)
                    value += "\n"
                else:
                    value += str(child)
                    value += "\n"

        if value[-1] == "\n":
            value = value[0:-1]

        return value

    def title(self, title=None):
        if title != None:
            self._title = title

        return self._title

    def color(self, color):
        self._param["color"] = color
        return self
    
    def shell(self, script, params=[], terminal=False):
        if script.find(" ") >= 0:
            self._param["shell"] = f"\"{script}\""
        else:
            self._param["shell"] = script

        param_index = 1
        for param in params:
            self._param[f"param{param_index}"] = param

        self._param["terminal"] = str(terminal).lower()

        return self

    def alternate(self, alt):
        if (alt):
            self._param["alternate"] = "true"
        
        return self
        
    def link(self, link):
        self._param["href"] = link
        return self

    def length(self, length):
        self._param["length"] = length
        return self

    def append_child(self, child):
        if isinstance(child, XbarItem) or isinstance(child, XbarSeperator):
            self._children.append(child)
        else:
            raise TypeError(f"Wrong type of child: {type(child)}")

class XbarSeperator():

    def __init__(self):
        return

class XbarPrinter:

    _default_config = XbarItem("Configure noti").shell("vi", ["$HOME/.noticonfig.json"], True)
    
    def __init__(self, conf):
        self._conf = conf
        self._root = XbarItem()
        self._configs = [self._default_config]
    
    def title(self, title=None):
        return self._root.title(title)
    
    def append_child(self, child):
        self._root.append_child(child)

    def print(self):
        if len(self._root._children) > 0:
            self.append_child(XbarSeperator())
        
        for config in self._configs:
            self.append_child(config)

        print(self._root)

    def add_error(self, title):
        self._configs.insert(0, XbarItem(title).color("red"))
    
    @classmethod
    def fatal(cls, message, help_link=None):
        root = XbarItem("Noti Error").color("red")

        messageItem = XbarItem(message)

        if help_link is not None:
            messageItem.link(help_link).color("red")
        
        root.append_child(messageItem)
        root.append_child(XbarSeperator())
        root.append_child(cls._default_config)

        print(root)
        
        exit(1)

    def generate_mr(self, mr):
        pipeline_color_map = {
            'success': 'green',
            'failed': 'red',
            'running': 'blue'
        }

        mr_item = XbarItem(level=2).link(mr.url)

        # pipeline field will be empty if it is cancelled
        failed_jobs = False
        if mr.ci_status in pipeline_color_map:
            mr_item.color(pipeline_color_map[mr.ci_status])
            if mr.ci_status == 'failed':
                failed_jobs = True
                mr_item.append_child(XbarItem("Failed jobs", level=3))
                for job in mr.failed_pipeline_jobs:
                    mr_item.append_child(XbarItem(job.name, level=3).color("red").link(job.url))
                
        title = mr.branch

        if len(mr.reviews) > 0:
            if failed_jobs:
                mr_item.append_child(XbarSeperator())
            mr_item.append_child(XbarItem(f"Discussions ({self.time_diff(mr.reviews[0].created_at)})", level=3))

            for review in mr.reviews:
                firstname = review.author.split(' ')[0]
                escaped_text = review.body.replace('-', '').replace('\n', '').replace('\r', '')
                mr_item.append_child(XbarItem(f"{firstname}: {escaped_text}", level=3).link(review.url).length(32))
            
            title += f" {self._conf.get('comments')}{len(mr.reviews)}"
        
        if mr.approved:
            title += ' ' + self._conf.get('approved')
        
        mr_item.title(title)
        
        self.append_child(mr_item)
        self.append_child(XbarItem(mr.title).color("white").alternate(True))

    def generate_title(self, mrs):
        statistics = {
            'approved': 0,
            'failed': 0,
            'running': 0,
            'comments': 0
        }
        pipeline_icon_map = {
            'failed': self._conf.get('failed'),
            'running': self._conf.get('running'),
            'comments': self._conf.get('comments'),
            'approved': self._conf.get('approved')
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
            title = self._conf.get('good_day')

        self.title(title)

    def time_diff(self, before):
        diff = (datetime.now().astimezone(tzlocal()) - before)
        seconds = diff.seconds
        days = diff.days

        if days > 365:
            return 'long long ago'
        elif days > 7:
            return f"{days} days ago"

        hours = int(seconds/3600)
        hours_text = ''
        if hours > 0:
            hours_text = f"{hours} hours"

        if days > 1:
            return f"{days} days {hours_text} ago"

        if hours > 0:
            hours_text += ' '

        minutes = int(seconds%3600/60)
        return f"{hours_text}{minutes} minutes ago"

try:
    from dateutil import parser
    from dateutil.tz import tzlocal
    from dateutil.tz import tzutc
except:
    XbarPrinter.fatal('Missing dependencies: You need to install python-dateutil', 'https://dateutil.readthedocs.io/en/stable/#installation')

def main(registry, conf, bp):
    vcs = []
    for s in registry:
        key = s.name.lower()
        if key in conf.user_config:
            try:
                vcs.append(s(conf.get_config(key)))
            except NotiError as e:
                bp.fatal(f"[{e.vcs}] {e.message}", e.help_link)

    if len(vcs) == 0:
        bp.fatal('You have to configure either gitlab or github')        

    mrs = {}

    from requests.exceptions import ConnectionError
    for v in vcs:
        try:
            mrs.update(v.get_mrs())   
        except ConnectionError:
            bp.add_error(f"{v.name}: failed to connect to the server")

    bp.generate_title(mrs)
    for repo_name, repo_mrs in mrs.items():
        if len(repo_mrs) == 0:
            continue

        bp.append_child(XbarItem(repo_name))
        for mr in repo_mrs:
            bp.generate_mr(mr)

    bp.print()

if __name__ == "__main__":
    conf = NotiConfig()
    bp = XbarPrinter(conf.emoji_config)
    registry = [Gitlab, Github]

    main(registry, conf, bp)