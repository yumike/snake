import inspect
import optparse
import os


class TaskNotFound(Exception):
    pass


class _TaskRegistry(object):

    def __init__(self):
        self._registry = {}

    def add(self, task):
        self._registry.setdefault(task.__class__, {})[task.name] = task

    def has_tasks_for(self, cls):
        return cls in self._registry and self._registry[cls]

    def get_tasks_for(self, cls):
        return self._registry.get(cls, {})

    def get(self, name, cls=None, create=False, fail_silently=False):
        registry = self._registry
        if cls:
            if cls in self._registry and name in self._registry[cls]:
                return self._registry[cls][name]
            if create:
                return cls(name)
        else:
            for tasks in registry.values():
                if name in tasks:
                    return tasks[name]
        if fail_silently:
            return
        raise TaskNotFound("%s %r was not found." % (cls.__name__, name))


registry = _TaskRegistry()


class BaseTask(object):

    def __init__(self, name, needs=None):
        self._func = None
        self.name = name
        self.prerequisites = []
        if needs:
            self.needs(*needs)
        registry.add(self)

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], '__call__'):
            self._func = args[0]
            return self
        return self.call(*args, **kwargs)

    def _prepare_prerequisites(self, tasks):
        prerequisites = []
        for task in tasks:
            if isinstance(task, basestring):
                name = task
            elif isinstance(task, BaseTask):
                name = task.name
            else:
                raise Exception("Uknown object type provided as prerequisite.")
            if name in self.prerequisites:
                raise Exception("%s already registered as prerequisite.")
            prerequisites.append(name)
        return prerequisites

    def needs(self, *tasks, **kwargs):
        replace = kwargs.get('replace', False)
        if self.prerequisites and not replace:
            raise Exception("%s already has some prerequisites.")
        self.prerequisites[:] = self._prepare_prerequisites(tasks)

    def also_needs(self, *tasks, **kwargs):
        if kwargs.get('prepend', False):
            self.prerequisites[0:0] = self._prepare_prerequisites(tasks)
        else:
            self.prerequisites.extend(self._prepare_prerequisites(tasks))

    def call(self):
        raise NotImplementedError

    def func(self):
        if self._func:
            if inspect.getargspec(self._func)[0]:
                self._func(self)
            else:
                self._func()


class Task(BaseTask):

    _called = set()

    def __init__(self, name, needs=None):
        super(Task, self).__init__(name, needs=needs)

    def call(self):
        if self.name not in self._called:
            self._called.add(self.name)
            for prerequisite in self.prerequisites:
                registry.get(prerequisite)()
            self.func()


class FileTask(BaseTask):

    def call(self):
        prerequisites_max_mtime = max(
            os.stat(prerequisite).st_mtime
            for prerequisite in self.prerequisites)
        if not os.path.exists(self.name)  or \
           os.stat(self.name).st_mtime < prerequisites_max_mtime:
            self.func()


class Command(BaseTask):

    usage = '%%prog [global_options] %s [options]'

    def __init__(self, name, needs=None, takes=None):
        super(Command, self).__init__(name, needs=needs)
        self.parser = optparse.OptionParser(usage=self.usage % self.name)
        if takes:
            self.takes(*takes)

    def _add_options(self, options):
        for option in options:
            if isinstance(option, (list, tuple)):
                dest = option[0]
                name = '--%s' % dest.replace('_', '-')
                help = option[1]
                self.parser.add_option(name, dest=dest, help=help)
            elif isinstance(option, optparse.Option):
                self.parser.add_option(option)
            else:
                raise Exception("Uknown object type provided as option.")

    def takes(self, *options, **kwargs):
        if not self.parser.option_list and not kwargs.get('replace', False):
            raise Exception("%s already has some prerequisites.")
        self.parser.option_list = []
        self._add_options(options)

    def also_takes(self, *options):
        self._add_options(options)

    def call(self, args):
        self.func(*self.parser.parse_args(args))

    def func(self, options, args):
        if self._func:
            arglen = len(inspect.getargspec(self._func)[0])
            if arglen == 3:
                self._func(self, options, args)
            elif arglen == 2:
                self._func(options, args)
            elif arglen == 1:
                self._func(args)
            else:
                self._func()


def task(*args, **kwargs):
    needs = kwargs.get('needs')
    if needs and not isinstance(needs, (list, tuple)):
        needs = [needs]
    def wrapper(func):
        if isinstance(func, Task):
            return func
        return Task(func.__name__, needs=needs)(func)
    if not args:
        return wrapper
    func = args[0]
    if hasattr(func, '__call__'):
        return wrapper(func)
    task = registry.get(func, cls=Task, create=True)
    if needs:
        task.needs(*needs)
    return task


def filetask(source, needs=None):
    task = registry.get(source, cls=FileTask, create=True)
    if needs:
        needs = needs if isinstance(needs, (list, tuple)) else [needs]
        task.needs(*needs)
    return task


def command(*args, **kwargs):
    needs = kwargs.get('needs')
    takes = kwargs.get('takes')
    if needs and not isinstance(needs, (list, tuple)):
        needs = [needs]
    def wrapper(func):
        if isinstance(func, Command):
            return func
        return Command(func.__name__, needs=needs, takes=takes)(func)
    if not args:
        return wrapper
    func = args[0]
    if hasattr(func, '__call__'):
        return wrapper(func)
    command = registry.get(func, cls=Command, create=True)
    if needs:
        command.needs(*needs)
    if takes:
        command.takes(*takes)
    return command
