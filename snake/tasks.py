import os


class TaskNotFound(Exception):
    pass


class _TaskRegistry(object):

    def __init__(self):
        self._registry = {}

    def add(self, task):
        self._registry.setdefault(task.__class__, {})[task.name] = task

    def get(self, name, cls=None, fail_silently=False):
        registry = self._registry
        if cls:
            if cls in self._registry and name in self._registry[cls]:
                return self._registry[cls][name]
        else:
            for tasks in registry.values():
                if name in tasks:
                    return tasks[name]
        if fail_silently:
            return
        raise TaskNotFound("%s %r was not found." % (cls.__name__, name))


registry = _TaskRegistry()


class DependencyList(list):

    def add(self, *deps):
        for dep in reversed(deps):
            if isinstance(dep, basestring):
                name = dep
            elif isinstance(dep, Task):
                name = dep.name
            else:
                raise Exception('Uknown object type provided as dependency.')
            if name in self:
                raise Exception('%s already registered as dependency.')
            self.insert(0, name)


class BaseTask(object):

    @classmethod
    def resolve(cls, name, local=True, create=False):
        try:
            return registry.get(name, cls if local else None)
        except TaskNotFound:
            if create:
                return cls(name)
            raise

    def __init__(self, name, deps=None):
        self.func = None
        self.name = name
        self.deps = DependencyList()
        if deps:
            self.deps.add(*deps)
        registry.add(self)

    def __call__(self, func=None):
        if hasattr(func, "__call__"):
            self.func = func
            return self
        return self.call()

    def call(self):
        raise NotImplementedError


class Task(BaseTask):

    _called = set()

    def __init__(self, name, deps=None):
        super(Task, self).__init__(name, deps=deps)

    def call(self):
        if self.name not in self._called:
            self._called.add(self.name)
            for dep in self.deps:
                registry.get(dep)()
            if self.func:
                self.func()


class FileTask(BaseTask):

    def call(self):
        if self.func:
            deps_max_mtime = max(os.stat(dep).st_mtime for dep in self.deps)
            if not os.path.exists(self.name)  or \
               os.stat(self.name).st_mtime < deps_max_mtime:
                self.func(self)


def task(*args, **kwargs):
    deps = kwargs.get('deps')
    if deps and not isinstance(deps, (list, tuple)):
        deps = [deps]
    def wrapper(func):
        if isinstance(func, Task):
            return func
        return Task(func.__name__, deps=deps)(func)
    if not args:
        return wrapper
    func = args[0]
    if hasattr(func, '__call__'):
        return wrapper(func)
    task = Task.resolve(func, create=True)
    if deps:
        task.deps.add(*deps)
    return task


def filetask(source, deps=None):
    task = FileTask.resolve(source, create=True)
    if deps:
        deps = deps if isinstance(deps, (list, tuple)) else [deps]
        task.deps.add(*deps)
    return task
