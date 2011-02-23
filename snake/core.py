import os
import subprocess
import sys
from contextlib import contextmanager


class Snake(object):

    def __init__(self):
        self.called = set()
        self.current_namespace = ''
        self.tasks = {}
        self.verbosity = 1

    def run_task(self, name):
        if name in self.called:
            return
        self.called.add(name)
        task = self.tasks[name]['func']
        if hasattr(task, 'depends_on'):
            for dep in task.depends_on:
                self.run_task(dep)
        task()

    def run(self, task_names):
        for name in task_names:
            self.run_task(name)

    def info(self, msg):
        if self.verbosity > 1:
            print(msg)

    def notice(self, msg):
        if self.verbosity > 0:
            print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print >> sys.stderr, "Error: %s" % msg

    def abort(self, msg):
        self.error(msg)
        sys.exit(1)

    @contextmanager
    def namespace(self, name):
        old_name = self.current_namespace
        self.current_namespace = '.'.join([old_name, name]).lstrip('.')
        yield
        self.current_namespace = old_name

    def task(self, f):
        name = '.'.join([self.current_namespace, f.__name__]).lstrip('.')
        self.tasks[name] = {'func': f, 'doc': f.__doc__}
        return f

    def depends_on(self, *tasks):
        def decorator(f):
            f.depends_on = tasks
            return f
        return decorator

    def sh(self, command, capture=False):
        kwargs = {'shell': True}
        if capture:
            kwargs['stdout'] = subprocess.PIPE
        self.notice("[sh] %s" % command)
        return subprocess.Popen([command], **kwargs).communicate()[0]
