import shlex
import subprocess


def sh(command, capture=False):
    kwargs = {"shell": True}
    if capture:
        kwargs['stdout'] = subprocess.PIPE
    return subprocess.Popen([command], **kwargs).communicate()[0]
