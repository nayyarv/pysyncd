# Pysyncd

A python esque replacement for [lsyncd](https://github.com/lsyncd/lsyncd) since it no longer works for OS X. Instead it uses [fswatch](https://github.com/emcrisostomo/fswatch) through the [pyfswatch](https://github.com/paul-nameless/pyfswatch) package.

Basically you get fswatch to watch a directory and on file changes, we create an rsync to send changed files over. This can work quite well for large directories since rsync'ing a whole dir can be tricky each time. It does an initial rsync to ensure files are the same. It's a one way sync so it's really designed to be used for working on a local machine and syncing code to a single remote dev machine.

Deletion is off by default and exclusions are kind of necessary for things like venvs/build folders

## Install

TODO: PR to pyfswatch
TODO: Make requirements.txt use a git/web install instead so the install is easier. 

1. Install fswatch. `brew install fswatch`
2. Checkout [my pyfswatch fork](https://github.com/nayyarv/pyfswatch) or download the zip. `git clone git@github.com:nayyarv/pyfswatch.git`
3. Optionally create a venv, but install the package `pip install -e /path/to/pyfswatch`. See [`requirements.txt`](requirements.txt) for my variant.

## Sample Config

This is mostly copied from the lsycnd, but pythonified.

TODO: convert to an actual json/yaml config so we can pass multiple versions over instead of a single type. It's basically already json (but has comments).

```python
settings = {
    "logfile": "/tmp/pysyncd.log",
    "level": "INFO"
}
sync = {
    "source": "<source dir>",
    "host": "<ip or .ssh/config entry if requires non default key>",
    "targetdir": "<dir on host>",
    "delay": 5, # interval between rsyncs
    "rsync": {
        "binary": "/usr/local/bin/rsync",
        "archive": True,
        "compress": True,
    },
    "exclude": ["build", "downloads", "venv", "venv35"]
}
```

## Notes/Limitations

1. Spawns an rsync for each file changed. Might choke on git checkout, testing needed.
2. You should configure a whole git checkout so the .git info can be synced over so branch info etc gets reflected for branch changes. 