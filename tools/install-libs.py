import sys
import pathlib
import shutil


"""
This script copies the python libraries from the format they are in the
micropython-lib git repo to a structure needed to make them importable
directly from micropython.

Usage e.g. as:
$ git clone https://github.com/micropython/micropython-lib.git
$ sudo python3 /tools/install-libs.py micropython-lib/micropython /usr/lib/micropython/
$ sudo python3 /tools/install-libs.py micropython-lib/micropython-stdlib /usr/lib/micropython/
$ ./micropthon

Alternatively any other path can be used to install the libraries, but it seems like
micropython does not support any PYTHONHOME like variable, but by cd:ing to the
library directory before running micropython we can get around this:

$ python3 /tools/install-libs.py micropython-lib/micropython /any/path/to/install/micropython-lib
$ python3 /tools/install-libs.py micropython-lib/micropython-stdlib /any/path/to/install/micropython-lib
$ cd /any/path/to/install/micropython-lib && ./micropthon
"""

IGNORE_LIBS = tuple()
IGNORE_FILES = ("setup.py",)


def copy_lib_files(src, dst):
    for child in src.glob("*.py"):
        if child.name not in IGNORE_FILES:
            shutil.copy(str(child), str(dst))


def install_single_lib(src, dst):
    # Some libraries are packed with suffix, e.g.:
    # umqtt.simple/umqtt/simple.py and
    # umqtt.robust/umqtt/robust.py
    # these should go in the same folder like:
    # umqtt/simple.py and umqtt/robust.py
    root_name = src.with_suffix("").name
    (dst / root_name).mkdir(exist_ok=True)
    copy_lib_files(src, dst / root_name)
    copy_lib_files(src / root_name, dst / root_name) # Might or might not exist


def install_libs(src, dst):
    dst.mkdir(exist_ok=True)
    for child in src.iterdir():
        if not child.is_dir() or child.name in IGNORE_LIBS:
            continue
        install_single_lib(child, dst)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("%s: Missing operands: SRC DST" % sys.argv[0])
        exit(1)

    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2])
    install_libs(src, dst)
