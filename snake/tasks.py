env = {
    'tasks': {},
    'called': set()
}


def resolve(name, create=False):
    try:
        return env['tasks'][name]
    except KeyError:
        if create:
            return Task(name)
        else:
            raise Exception('Task %r was not found.' % name)


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


class Task(object):

    def __init__(self, func, deps=None):
        if isinstance(func, basestring):
            self.func = None
            self.name = func
        else:
            self.func = func
            self.name = func.__name__
        self.deps = DependencyList()
        if deps:
            self.deps.add(*deps)
        env["tasks"][self.name] = self

    def __call__(self):
        if self.name not in env['called']:
            env['called'].add(self.name)
            for dep in self.deps:
                resolve(dep)()
            if self.func:
                self.func()

    def __str__(self):
        return self.name


def task(*args, **kwargs):
    deps = kwargs.get('deps')
    if deps and not isinstance(deps, (list, tuple)):
        deps = [deps]
    def wrapper(func):
        return func if isinstance(func, Task) else Task(func, deps=deps)
    if not args:
        return wrapper
    func = args[0]
    if hasattr(func, '__call__'):
        return wrapper(func)
    task = resolve(func, create=True)
    if deps:
        task.deps.add(*deps)
    return task