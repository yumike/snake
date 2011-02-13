import subprocess
from snake import state


def not_a_task(f):
    f.not_a_task = True
    return f


def depends_on(*tasks):
    def decorator(f):
        f.depends_on = tasks
        return f
    return decorator


def sh(command, cwd=False, capture=False):
    kwargs = {'shell': True}
    if capture:
        kwargs['stdout'] = subprocess.PIPE
    if not cwd:
        kwargs['cwd'] = state.basepath
    return subprocess.Popen(command, **kwargs).communicate()[0]
