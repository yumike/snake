import subprocess
import sys

from snake import state


def info(msg):
    if state.verbosity > 0:
        print(msg)


def debug(msg):
    if state.verbosity > 1:
        print(msg)


def error(msg):
    print >> sys.stderr, "Error: %s" % msg


def abort(msg):
    error(msg)
    sys.exit(1)


def sh(command, capture=False):
    kwargs = {'shell': True}
    if capture:
        kwargs['stdout'] = subprocess.PIPE
    info("[sh] %s" % command)
    return subprocess.Popen([command], **kwargs).communicate()[0]
