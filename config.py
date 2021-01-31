settings = {
    "logfile": "/tmp/lsyncd.log",
    "statusFile": "/tmp/lsyncd.status",
    "nodaemon": True,
}
sync = {
    "default.rsyncssh": None,
    "source": "/Users/varun/ACBookPro",
    "host": "13.55.249.70",
    "targetdir": "/home/varun/ACBookPro",
    "delay": 5,
    "rsync": {
        "binary": "/usr/local/bin/rsync",
        "archive": True,
        "compress": True,
    },
    "exclude": {"build", "downloads", "venv", "venv35"},
    "ssh": {
        "identityFile": "/Users/varun/.ssh/id_ed25519",
        "options": {"User": "varun"},
    },
}
