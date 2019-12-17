# Noti
Noti is a Mac OS X menu bar plugin to show the status of pull requests

## Installation
1. Noti is distributed as a plugin of [bitbar](https://getbitbar.com/). Please follow the guidance to install bitbar first.

1. After you have bitbar installed, you can simply download [`noti.py`](https://raw.githubusercontent.com/ye11ow/noti/master/noti.py) and put it under your bitbar plugin folder.

1. Edit `noti.py`. 
    1. On the first line, make sure you point to the right Python interpreter path.
    1. Make sure you update all the default settings in `user_config` section.
    1. You may need to run `pip install python-dateutil` and `sudo pip install --upgrade python-gitlab` to install the dependencies.

1. Rename the `noti.py` to `noti.{time}.py`. The `{time}` is the refresh rate. For instance, `noti.30s.py` will refresh the status every 30 seconds. For detailed instruction, you can refer to https://github.com/matryer/bitbar#configure-the-refresh-time.

1. Done!

## Features

### Supported VCS

- [X] Gitlab + Gitlab pipeline
- [ ] Github

### Supported GUI

- [X] Bitbar
- [ ] VS Code
- [ ] Terminal ([WTF](https://wtfutil.com/) maybe?)
