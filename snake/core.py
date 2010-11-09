import optparse
import subprocess
import sys

from contextlib import contextmanager

from snake.namespace import Namespace
from snake.tasks import Command, File, Task


class Snake(object):

    def __init__(self, usage="%prog [options] [task] ..."):
        self.verbosity = 1
        self.tasks = Namespace('', self)
        self.current_namespace = self.tasks
        self.files = {}
        self.called = set()
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.disable_interspersed_args()
        self.set_parser_options()

    def set_parser_options(self):
        self.parser.add_option(
            '-v', '--verbose', action='store_true', dest='verbose', default=False,
            help="give more output")
        self.parser.add_option(
            '-q', '--quiet', action='store_true', dest='quiet', default=False,
            help="give less output")

    def find(self, name, fail_silently=False):
        if name in self.files:
            return self.files[name]
        item = self.tasks.find(name.split(':'), fail_silently=fail_silently)
        if isinstance(item, Namespace):
            item = item.find(['default'], fail_silently=fail_silently)
        return item

    @contextmanager
    def namespace(self, name):
        if name not in self.current_namespace:
            self.current_namespace.add(Namespace(name, self))
        elif not isinstance(Namespace, self.current_namespace[name]):
            raise Exception("%r already exists as task" % name)
        parent_namespace = self.current_namespace
        self.current_namespace = self.current_namespace[name]
        yield self.current_namespace
        self.current_namespace = parent_namespace

    def task(self, *args, **kwargs):
        depends_on = kwargs.get('depends_on')
        if depends_on and not isinstance(depends_on, (list, tuple)):
            depends_on = [depends_on]
        def wrapper(func):
            if isinstance(func, Task):
                return func
            if self.current_namespace.path:
                name = ':'.join([self.current_namespace.path, func.__name__])
            else:
                name = func.__name__
            task = Task(name, self, prerequisites=depends_on, func=func)
            self.current_namespace.add(task)
            return task
        if not args:
            return wrapper
        arg = args[0]
        if hasattr(arg, '__call__'):
            return wrapper(arg)
        task = self.current_namespace.resolve(arg, cls=Task, create=True)
        if depends_on:
            task.depends_on(*depends_on)
        return task

    def file(self, name, depends_on=None):
        if depends_on and not isinstance(depends_on, (list, tuple)):
            depends_on = [depends_on]
        def wrapper(func):
            if isinstance(func, File):
                return func
            file = File(name, self, prerequisites=depends_on, func=func)
            self.files[name] = file
            return file
        return wrapper

    def command(self, *args, **kwargs):
        depends_on = kwargs.get('depends_on')
        if depends_on and not isinstance(depends_on, (list, tuple)):
            depends_on = [depends_on]
        takes = kwargs.get('takes')
        if takes:
            is_single_option = (
                not isinstance(takes, (list, tuple)) or
                not isinstance(takes[0], (optparse.Option, list, tuple)))
            if is_single_option:
                takes = [takes]
        def wrapper(func):
            if isinstance(func, Command):
                return func
            if self.current_namespace.path:
                name = ':'.join([self.current_namespace.path, func.__name__])
            else:
                name = func.__name__
            command = Command(name, self, prerequisites=depends_on,
                              options=takes, func=func)
            self.current_namespace.add(command)
            return command
        if not args:
            return wrapper
        arg = args[0]
        if hasattr(arg, '__call__'):
            return wrapper(arg)
        command = self.current_namespace.resolve(arg, cls=Command, create=True)
        if depends_on:
            command.depends_on(*depends_on)
        if takes:
            command.takes(*takes)
        return command

    def run(self, args=None):
        if args is None:
            args = sys.argv[1:]
        options, args = self.parser.parse_args(args)
        if options.verbose:
            self.verbosity += 1
        if options.quiet:
            self.verbosity -= 1
        if not args:
            args = ['default']
        while args:
            name = args.pop(0)
            task = self.find(name, fail_silently=True)
            if not task:
                self.abort("task %r was not found." % name)
            if isinstance(task, Command):
                task(args)
                sys.exit()
            else:
                task()

    def info(self, msg):
        if self.verbosity > 1:
            print(msg)

    def warning(self, msg):
        if self.verbosity > 0:
            print(msg)

    def error(self, msg):
        print >> sys.stderr, "Error: %s" % msg

    def abort(self, msg):
        self.error(msg)
        sys.exit(1)

    def sh(self, command, capture=False):
        kwargs = {'shell': True}
        if capture:
            kwargs['stdout'] = subprocess.PIPE
        self.info("[sh] %s" % command)
        return subprocess.Popen([command], **kwargs).communicate()[0]
