import os
import pathlib
import tempfile

import pexpect

from typing import Union


def read_config(path: Union[pathlib.Path, str]):
    fullc = []
    with open(path, "r") as f:
        fullconfig = f.read().replace("=", ":")
        print(fullconfig)


if __name__ == "__main__":
    read_config(os.path.expanduser("~/.lsyncd"))
