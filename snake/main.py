import os
import sys

from snake.core import Snake


SNAKEFILE_LOADED = False


def abort(msg):
    print >> sys.stderr, "Error: %s" % msg
    sys.exit(1)


def load_snakefile(path, fail_silently=False):
    global SNAKEFILE_LOADED
    if not SNAKEFILE_LOADED:
        sys.path.insert(0, path)
        try:
            return __import__('snakefile')
        except ImportError:
            if not fail_silently:
                abort("couldn't find any snakefile.")
        else:
            SNAKEFILE_LOADED = True
        del sys.path[0]


def find_snakefile():
    global SNAKEFILE_LOADED
    path = os.getcwd()
    while True:
        filepath = os.path.join(path, 'snakefile.py')
        if os.path.isfile(filepath):
            return load_snakefile(path), filepath
        if not os.path.split(path)[1]:
            break
        path = os.path.split(path)[0]
    if not SNAKEFILE_LOADED:
        abort("couldn't find any snakefile.")


def main():
    snakefile, snakefilepath = find_snakefile()
    for name in dir(snakefile):
        attr = getattr(snakefile, name)
        if isinstance(attr, Snake):
            attr.run(snakefilepath)
            break
    else:
        abort("couldn't find any Snake instance in snakefile.")
