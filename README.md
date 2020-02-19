# Noti

[![Build Status](https://travis-ci.org/ye11ow/noti.svg?branch=master)](https://travis-ci.org/ye11ow/noti)
[![Coverage Status](https://coveralls.io/repos/github/ye11ow/noti/badge.svg?branch=master)](https://coveralls.io/github/ye11ow/noti?branch=master)

Noti is a Mac OS X menu bar plugin to show the status of pull requests. It is distributed as a plugin of [bitbar](https://getbitbar.com/).

## Installation
1. Make sure both `bitbar` and `python3` are installed on your machine.

1. Clone this repo or just download [`noti.py`](https://raw.githubusercontent.com/ye11ow/noti/master/noti.py) and put it under your bitbar plugin folder. (You may want to edit the shebang of `noti.py` to make sure it points to the right Python interpreter)

1. Rename the `noti.py` to `noti.{time}.py`. The `{time}` is the refresh rate. For instance, `noti.30s.py` will refresh the status every 30 seconds. For detailed instruction, you can refer to https://github.com/matryer/bitbar#configure-the-refresh-time.

1. You should be able to see noti on your menu. Please follow the guide to install the dependencies if you have seen the `Missing dependencies` error.

1. Configure noti to connect to your Gitlab or Github. You can either edit the config file under `$HOME/.noticonfig.json` or select `Configure noti` on the dropdown menu. Please refer to the Configurations section

## Configurations

```javascript
// Current Noti only supports 1 VCS at a time. You CANNOT configure both gitlab and github.
// Make sure you remove all the comments before saving the .noticonfig.json file
{
    // Gitlab related configurations
    "gitlab": {
        //  Go to the "User Settings" -> "Access Tokens" page, create a Personal Access Token with "api" Scopes
        "token": "",

        //  Go to the home page of the repo, you will find the Project ID under the name of the repo (in grey).
        "project_id": [],

        //  The host of the gitlab server. e.g. https://gitlab.example.com
        "host": "",
    },

    //  Github related configurations
    "github": {
        //  Go to Github "Settings" -> "Developer settings" -> "Personal access tokens" and "Generate new token" with "repo" scopes
        "token": "",

        //  The name of the repo, e.g. "ye11ow/noti"
        "repo": []
    }
}
```

## Features

### Supported VCS

- [X] Gitlab + Gitlab pipeline
- [X] Github + Travis CI
- [ ] Bitbucket + Bitbucket pipeline

### Supported GUI

- [X] Bitbar
- [ ] Native Mac app
- [ ] VS Code
- [ ] Terminal ([WTF](https://wtfutil.com/) maybe?)
