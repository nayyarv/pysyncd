#!/usr/bin/env python3
import time
import subprocess
import logging

import pexpect

import config

kwargs = {}

if "logfile" in config.settings:
    kwargs = {
        "handlers": [
            logging.FileHandler(config.settings["logfile"]),
            logging.StreamHandler(),
        ]
    }

logging.basicConfig(
    level=getattr(logging, config.settings.get("level", "INFO")),
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
    datefmt="%Y%m%d %H:%M:%S",
    **kwargs,
)
logger = logging.getLogger("pysyncd")


def check_config(sync):
    for field in ["source", "targetdir"]:
        if not sync[field].endswith("/"):
            sync[field] = sync[field] + "/"


def build_rysnc(sync=config.sync) -> [str]:
    cmd = []
    cmd.append(sync["rsync"]["binary"])
    if sync.get("nfs_optimised"):
        cmd.extend("--numeric-ids --omit-dir-times --whole-file".split())
        cmd.extend(["-T", "/data/scratch/varun"])
    if sync["rsync"]["archive"]:
        cmd.append("-a")
    if sync["rsync"]["compress"]:
        cmd.append("-z")
    for exclude in sync["exclude"]:
        cmd.extend(["--exclude", exclude])

    logger.debug("Rsync command is %s", cmd)
    cmd.extend(
        [config.sync["source"], f"{config.sync['host']}:{config.sync['targetdir']}"]
    )
    return cmd


def build_fswatch(sync=config.sync) -> [str]:
    cmd = ["/usr/local/bin/fswatch", "-o", sync["source"]]
    for exclude in sync["exclude"]:
        cmd.extend(["--exclude", exclude])
    for exclude in ["*.lock"]:
        cmd.extend(["--exclude", exclude])
    logger.debug("Fswatch cmd is %s", " ".join(cmd))
    return cmd


def pex_readlines(child: pexpect.spawn) -> int:
    try:
        return int(child.readline().strip())
    except pexpect.TIMEOUT:
        return 0
    except pexpect.EOF:
        raise RuntimeError("Pexpect has shut down unexpectedly")


def timeloop(interval=5):
    from math import ceil

    while True:
        before = time.time()
        yield
        after = time.time()
        to_sleep = ceil(max(0, interval - (after - before)))
        logger.debug("Sleeping for %d", to_sleep)
        time.sleep(to_sleep)


def main():
    check_config(config.sync)
    base_rsync = build_rysnc()

    logger.info("Running initial rsync %s", " ".join(base_rsync))
    subprocess.run(base_rsync, check=True)

    fswatcher = build_fswatch()
    logger.info("Initial sync over, starting watch sync %s", fswatcher)

    child = pexpect.spawn(fswatcher[0], fswatcher[1:], timeout=1, encoding="utf-8")
    for _ in timeloop(config.sync.get("interval", 5)):
        all_lines = pex_readlines(child)
        if all_lines:
            logger.info("Seen %d files change, running rsync", all_lines)
            subprocess.run(base_rsync, check=True)
            logger.info("Rsync over")


if __name__ == "__main__":
    main()
