# Noti

[![Build Status](https://github.com/ye11ow/noti/actions/workflows/python-app.yml/badge.svg)](https://github.com/ye11ow/noti/actions)
[![Coverage Status](https://coveralls.io/repos/github/ye11ow/noti/badge.svg?branch=main)](https://coveralls.io/github/ye11ow/noti?branch=main)

Noti is a Mac OS X menu bar plugin to show the status of pull requests (merge requests). It is distributed as a plugin of [xbar](https://xbarapp.com/)(former **Bitbar**).

![Tutorial](https://github.com/ye11ow/noti/blob/main/docs/images/Bitbar.png?raw=true)

* The background color indicate the status of the CI job behind this pull request
    * <font color="Green">Green</font>: Job passed
    * <font color="blue">Blue</font>: Job is running
    * <font color="red">Red</font>: Job failed
* Emojis:
    * 👍: Pull request is approved (or approval is optional)
    * 🏃: The CI job is running
    * 🙃: Number of pull requests that failed the CI job
    * 💬: Number of pull reuqest comments

## Installation
1. Make sure both `xbar` and `python3` (>=3.6) are installed on your machine.

1. Clone this repo and move `noti.py` to your xbar plugin folder as `noti.{time}.py`. The `{time}` is the refresh interval. For instance, renaming to `noti.30s.py` will lead to a  30 seconds' refresh interval. For detailed instruction, you can refer to https://github.com/matryer/xbar-plugins/blob/main/CONTRIBUTING.md#configure-the-refresh-time.

1. Edit the shebang of `noti.{time}.py` to make sure it points to the right Python interpreter (default `/usr/local/bin/python3`). 

1. Install the python dependencies `/usr/local/bin/python3 -m pip install -r requirements.txt`.

1. Configure noti to connect to your Gitlab or Github. You can either edit the config file under `$HOME/.noticonfig.json` or select `Configure noti` on the dropdown menu. Please refer to the Configurations section for details.

1. You should be able to see the status on your menubar if everything is setup properly. Enjoy!😃.

## Configurations

```javascript
// Noti will automatically create this file under $HOME/.noticonfig.json if it doesn't exist
{
    // Gitlab related configurations
    "gitlab": {
        // [REQUIRED] Go to the "User Settings" -> "Access Tokens" page, create a Personal Access Token with "api" Scopes
        "token": "",

        // [REQUIRED] Go to the home page of the repo, you will find the Project ID under the name of the repo (in grey).
        "project_id": [],

        // [Optional] The host of the gitlab server. Leave it empty to use the public Gitlab server.
        "host": "",

        // [Optional] Filters
        "filters": {
            
            // Filter by the usernames. The username here is the @ ID
            "usernames": []
        }
    },

    // Github related configurations
    "github": {
        // [REQUIRED] Go to Github "Settings" -> "Developer settings" -> "Personal access tokens" and "Generate new token" with "repo" scopes
        "token": "",

        // [REQUIRED] The name of the repo. e.g. "ye11ow/noti"
        "repo": [],

        // [Optional] The host of the github server. Leave it empty to use the public Github server.
        "host": "",

        // [Optional] Filters
        "filters": {
            
            // Filter by the usernames. The username here is the ID. e.g. https://github.com/ye11ow ye11ow is the username.
            "usernames": []
        }
    },

    // [Optional] Customize the emoji
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
- [ ] Github + Github Action
- [ ] Bitbucket + Bitbucket pipeline

### Supported GUI

- [X] xbar
- [ ] Native Mac app
- [ ] VS Code
- [ ] Terminal ([WTF](https://wtfutil.com/) maybe?)
