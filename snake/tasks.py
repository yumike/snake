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
        self.func = None
        self.name = name
        self.prerequisites = []
        if needs:
            self.needs(*needs)
        registry.add(self)

    def __call__(self, func=None):
        if hasattr(func, '__call__'):
            self.func = func
            return self
        return self.call()

    def _prepare_prerequisites(self, tasks):
        prerequisites = []
        for task in tasks:
            if isinstance(task, basestring):
                name = task
            elif isinstance(task, BaseTask):
                name = task.name
            else:
                print task
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


class Task(BaseTask):

    _called = set()

    def __init__(self, name, needs=None):
        super(Task, self).__init__(name, needs=needs)

    def call(self):
        if self.name not in self._called:
            self._called.add(self.name)
            for prerequisite in self.prerequisites:
                registry.get(prerequisite)()
            if self.func:
                self.func()


class FileTask(BaseTask):

    def call(self):
        if self.func:
            prerequisites_max_mtime = max(
                os.stat(prerequisite).st_mtime
                for prerequisite in self.prerequisites)
            if not os.path.exists(self.name)  or \
               os.stat(self.name).st_mtime < prerequisites_max_mtime:
                self.func(self)


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
