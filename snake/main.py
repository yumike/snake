import os
import sys

from snake.tasks import env


def load_snakefile():
    cwd = os.getcwd()
    sys.path.insert(0, cwd)
    try:
        imported = __import__('snakefile')
    except ImportError:
        print >> sys.stderr, "Error: couldn't find any snakefiles."
        exit(1)
    del sys.path[0]


def main():
    args = sys.argv[1:]
    load_snakefile()
    name = args[0] if args else 'default'
    task = env["tasks"].get(name)
    if not task:
        print >> sys.stderr, "Error: task %r was not found." % name
        exit(1)
    task()