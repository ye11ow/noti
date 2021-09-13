# Noti

[![Build Status](https://github.com/ye11ow/noti/actions/workflows/python-app.yml/badge.svg)](https://github.com/ye11ow/noti/actions)
[![Coverage Status](https://coveralls.io/repos/github/ye11ow/noti/badge.svg?branch=main)](https://coveralls.io/github/ye11ow/noti?branch=main)

Noti is a Mac OS X menu bar plugin to show the status of pull requests (merge requests). It is distributed as a plugin of [xbar](https://xbarapp.com/)(former **bitbar**).

![Tutorial](https://github.com/ye11ow/noti/blob/main/docs/images/Bitbar.png?raw=true)

* The background color indicate the status of the CI job behind this pull request
    * <font color="Green">Green</font>: Job passed
    * <font color="blue">Blue</font>: Job is running
    * <font color="red">Red</font>: Job failed
* Emojis:
    * 👍: Pull request is approved
    * 🏃: The CI job is running
    * 🙃: Number of pull requests that failed the CI job
    * 💬: Number of pull reuqest comments

## Installation
1. Make sure both `xbar` and `python3` (>=3.6) are installed on your machine.

1. Clone this repo or just download [`noti.py`](https://raw.githubusercontent.com/ye11ow/noti/main/noti.py) and put it under your xbar plugin folder. (You may want to edit the shebang of `noti.py` to make sure it points to the right Python interpreter)

1. Rename the `noti.py` to `noti.{time}.py`. The `{time}` is the refresh rate. For instance, `noti.30s.py` will refresh the status every 30 seconds. For detailed instruction, you can refer to https://github.com/matryer/xbar#configure-the-refresh-time.

1. Configure noti to connect to your Gitlab or Github. You can either edit the config file under `$HOME/.noticonfig.json` or select `Configure noti` on the dropdown menu. Please refer to the Configurations section for details.

1. Make sure you have the following dependencies installed (depend on which VCS you want to use) and you should be able to see the status on your menubar.

* `pip install python-dateutil` (always install this)
* `sudo pip install --upgrade python-gitlab` (for Gitlab)
* `pip install PyGithub` (for Github)

## Configurations

```javascript
// Noti will automatically create this file under $HOME/.noticonfig.json if it doesn't exist
{
    // Gitlab related configurations
    "gitlab": {
        // Go to the "User Settings" -> "Access Tokens" page, create a Personal Access Token with "api" Scopes
        "token": "",

        // Go to the home page of the repo, you will find the Project ID under the name of the repo (in grey).
        "project_id": [],

        // [Optional] The host of the gitlab server. Leave it empty to use the public Gitlab server.
        "host": "",

        // [Optional] Filters
        "filters": {
            
            // [Optional] Filter by the usernames. The username here is the @ ID
            "usernames": []
        }
    },

    // Github related configurations
    "github": {
        // Go to Github "Settings" -> "Developer settings" -> "Personal access tokens" and "Generate new token" with "repo" scopes
        "token": "",

        // The name of the repo. e.g. "ye11ow/noti"
        "repo": [],

        // [Optional] The host of the github server. Leave it empty to use the public Github server.
        "host": "",

        // [Optional] Filters
        "filters": {
            
            // [Optional] Filter by the usernames. The username here is the ID. e.g. https://github.com/ye11ow ye11ow is the username.
            "usernames": []
        }
    },

    // Customize the emoji
    "emoji": {

        // Show on the title when there isn't any status
        "good_day": "😃",

        // The MR is approved
        "approved": "👍",

        // The pipeline behind this MR is currently running
        "running": "🏃",

        // The pipeline is failed
        "failed": "🙃",

        // Number of comments
        "comments": "💬"
    }
}
```

## Features

### Supported VCS

- [X] Gitlab + Gitlab pipeline
- [X] Github + Travis CI
- [ ] Bitbucket + Bitbucket pipeline

### Supported GUI

- [X] xbar
- [ ] Native Mac app
- [ ] VS Code
- [ ] Terminal ([WTF](https://wtfutil.com/) maybe?)


### This is a test PR