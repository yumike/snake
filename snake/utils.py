import shlex
import subprocess


def sh(command, capture=False):
    args = shlex.split(command)
    kwargs = {}
    if capture:
        kwargs['stdout'] = subprocess.PIPE
    p = subprocess.Popen(args, **kwargs)
    return p.communicate()[0]
