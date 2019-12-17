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

import gitlab
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import datetime

# Put your personal configuration here
user_config = {
    # Go to the "User Settings" -> "Access Tokens" page, create a Personal Access Token with "api" Scopes
    'token': '',

    # Go to the home page of the repo, you will find the Project ID under the name of the repo (in grey).
    'project_id': [],

    # The host of the gitlab server. e.g. https://gitlab.example.com
    'gitlab_host': '',
}

class Gitlab:
    def __init__(self, config):
        self._config = config
        self._gl = gitlab.Gitlab(config['gitlab_host'], private_token=config['token'])

    def get_mrs(self):
        mrs = []

        for pid in user_config['project_id']:
            project = self._gl.projects.get(pid)
            for list_mr in project.mergerequests.list(state='opened'):
                mrs.append(MR(project, list_mr))

        return mrs


class MR:
    def __init__(self, project, list_mr):
        self._project = project
        self._mr = self._project.mergerequests.get(list_mr.get_id())

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
            self._reviews = list(map(lambda x: Review(self, x), reviews))

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

class Review:
    def __init__(self, mr, review):
        self._mr = mr
        self._review = review

    @property
    def author(self):
        return self._review.attributes.get('author')['name']

    @property
    def created_at(self):
        return self._review.attributes.get('created_at')

    @property
    def body(self):
        return self._review.attributes.get('body')

    @property
    def url(self):
        return f"{self._mr.url}#note_{self._review.get_id()}"

class BitbarPrinter:
    def __init__(self):
        pass

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
            sub_text += '-----\n'

            last = mr.reviews[0].created_at
            diff = datetime.now().astimezone(tzlocal()) - parser.parse(last).astimezone(tzlocal())

            sub_text += f"--Discussions ({diff})\n"

            for review in mr.reviews:
                firstname = review.author.split(' ')[0]
                short = review.body.replace('-', '').replace('\n', '')
                short = short[:32]
                sub_text += f"--{firstname}: {short} | href={review.url}\n"

        if len(mr.reviews) == 0:
            title = f"{mr.branch} {title}"
        else:
            title = f"{mr.branch} 💬{len(mr.reviews)} {title}"

        title += '\n'

        print(f"{title}\n\n{sub_text}")

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


if __name__== "__main__":
    gl = Gitlab(user_config)
    mrs = gl.get_mrs()

    bp = BitbarPrinter()
    bp.print_title(mrs)
    for mr in mrs:
        bp.print_mr(mr)
