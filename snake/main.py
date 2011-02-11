import imp
import os
import sys
from snake.core import Snake


def abort(msg):
    print >> sys.stderr, "Error: %s" % msg
    sys.exit(1)


def get_ascending_paths(path):
    paths = []
    while True:
        paths.append(path)
        path, tail = os.path.split(path)
        if not tail:
            break
    return paths


def find_snakefile():
    paths = get_ascending_paths(os.getcwd())
    try:
        return imp.find_module('snakefile', paths)
    except:
        abort("couldn't find any snakefile.")


def get_snakefile():
    return imp.load_module('snakefile', *find_snakefile())


def main():
    snakefile = get_snakefile()
    for name in dir(snakefile):
        attr = getattr(snakefile, name)
        if isinstance(attr, Snake):
            attr.run(snakefile.__file__)
            break
    else:
        abort("couldn't find any Snake instance in snakefile.")
