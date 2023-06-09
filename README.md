# Pysyncd

A replacement for lsyncd on os x since it's dev/fsevents interface doesn't seem to work

This uses fswatch as a replacement. 


## Sample Config

This is mostly copied from the lsycnd, but pythonified

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
