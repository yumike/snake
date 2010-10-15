import subprocess


def sh(command, capture=False):
    kwargs = {"shell": True}
    if capture:
        kwargs['stdout'] = subprocess.PIPE
    print("[sh] %s" % command)
    return subprocess.Popen([command], **kwargs).communicate()[0]
