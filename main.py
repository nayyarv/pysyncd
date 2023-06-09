#!/usr/bin/env python3
import subprocess
import logging
import os.path

from typing import List

import fswatch

# custom python code with the config needed
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


def validated_config(sync):
    """Fixes up config as expected"""
    for field in ["source", "targetdir"]:
        if not sync[field].endswith("/"):
            sync[field] = sync[field] + "/"
    sync["source"] = os.path.expanduser(sync["source"])


def base_rsync(sync=config.sync) -> [str]:
    cmd = []
    cmd.append(sync["rsync"]["binary"])
    if sync.get("nfs_optimised"):
        cmd.extend("--numeric-ids --omit-dir-times --whole-file".split())
        # dont need this since we're not hitting a network drive
        cmd.extend(["-T", "/data/varun"])
    if sync["rsync"]["archive"]:
        cmd.append("-a")
    if sync["rsync"]["compress"]:
        cmd.append("-z")
    for exclude in sync["exclude"]:
        cmd.extend(["--exclude", exclude])

    logger.debug("Rsync command is %s", cmd)
    return cmd

def init_rsync(base_cmd: List[str], sync=config.sync) -> [str]:
    return base_cmd + [
        config.sync["source"], f"{config.sync['host']}:{config.sync['targetdir']}" 
    ]
    

def file_rsync(base_cmd: List[str], filepath: str, sync=config.sync) -> [str]:
    """use for a file specific rsync"""
    relpath = os.path.relpath(filepath, sync['source'])
    destpath = os.path.join(sync['targetdir'], relpath)
    return base_cmd + [
        filepath, f"{config.sync['host']}:{destpath}"
    ]



def main():
    validated_config(config.sync)
    base_cmd = base_rsync()
    init_sync_cmd = init_rsync(base_cmd)

    logger.info("Running initial rsync %s", " ".join(init_sync_cmd))
    subprocess.run(init_sync_cmd, check=True)
    logger.info("Rsync over, starting watch command")

    monitor = fswatch.Monitor()
    monitor.add_path(config.sync["source"])

    def callb(path: bytes, *args):
        """ 
        Full callback signature. flags type might not be correct.
        def callback(path: bytes, evt_time: int, flags: List[int], flags_num: int):
            print(path.decode(), evt_time, flags_num, event_num)

        """
        filepath = path.decode()
        fl_cmd = file_rsync(base_cmd, filepath)
        logger.debug("Running file rsync %s", " ".join(fl_cmd))
        subprocess.run(fl_cmd, check=True)
        logger.debug("Finished %s sync", filepath)

    monitor.set_callback(callb)
    monitor.start()


if __name__ == "__main__":
    main()
