import os
import pathlib
import time
import subprocess
import logging


from typing import Union

import pexpect

import config

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
    datefmt="%Y%m%d %H:%M:%S",
)
logger = logging.getLogger("pysyncd")


def build_rysnc(sync=config.sync) -> [str]:
    cmd = []
    cmd.append(sync["rsync"]["binary"])
    cmd.append("-C")
    if sync["rsync"]["archive"]:
        cmd.append("-a")
    if sync["rsync"]["compress"]:
        cmd.append("-z")
    for exclude in sync["exclude"]:
        cmd.append(f"--exclude '{exclude}'")
    cmd.append(sync["source"])
    cmd.append(f"{sync['host']}:{sync['targetdir']}")
    logger.debug("Rsync command is %s", cmd)
    return cmd


def build_fswatch(sync=config.sync) -> [str]:
    cmd = ["/usr/local/bin/fswatch", sync["source"]]
    for exclude in sync["exclude"]:
        cmd.append(f"--exclude '{exclude}'")
    logger.debug("Fswatch cmd is %s", " ".join(cmd))
    return cmd


def read_config(path: Union[pathlib.Path, str]):
    fullc = []
    with open(path, "r") as f:
        fullconfig = f.read().replace("=", ":")
        print(fullconfig)


def pex_readlines(child: pexpect.spawn):
    lines_read = []
    try:
        while True:
            lines_read.append(child.readline().strip())
    except pexpect.TIMEOUT:
        logger.debug("Read %d lines", len(lines_read))
        return lines_read
    except pexpect.EOF:
        raise RuntimeError("Pexpect has shut down unexpectedly")


def main():
    fswatcher = build_fswatch()
    child = pexpect.spawn(" ".join(fswatcher), timeout=5)
    for i in range(10):
        all_lines = pex_readlines(child)
        logger.debug("Sleeping for 5 seconds")
        time.sleep(5)


if __name__ == "__main__":
    main()
