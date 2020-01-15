# Noti

[![Build Status](https://travis-ci.org/ye11ow/noti.svg?branch=master)](https://travis-ci.org/ye11ow/noti)
[![Coverage Status](https://coveralls.io/repos/github/ye11ow/noti/badge.svg?branch=master)](https://coveralls.io/github/ye11ow/noti?branch=master)

Noti is a Mac OS X menu bar plugin to show the status of pull requests

## Installation
1. Noti is distributed as a plugin of [bitbar](https://getbitbar.com/). Please follow the guidance to install bitbar first.

1. After you have bitbar installed, you can simply download [`noti.py`](https://raw.githubusercontent.com/ye11ow/noti/master/noti.py) and put it under your bitbar plugin folder.

1. Edit `noti.py`: make sure you point to the right Python interpreter path in shebang.

1. Edit `$HOME/.noticonfig.json`: make sure you configure noti properly.

1. You may need to follow the instruction to install the dependencies if you have seen the `Missing dependencies` error.

1. Rename the `noti.py` to `noti.{time}.py`. The `{time}` is the refresh rate. For instance, `noti.30s.py` will refresh the status every 30 seconds. For detailed instruction, you can refer to https://github.com/matryer/bitbar#configure-the-refresh-time.

1. Done!

## Features

### Supported VCS

- [X] Gitlab + Gitlab pipeline
- [X] Github
    - [ ] Travis CI

### Supported GUI

- [X] Bitbar
- [ ] Native Mac app
- [ ] VS Code
- [ ] Terminal ([WTF](https://wtfutil.com/) maybe?)
