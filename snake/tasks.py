env = {
    'tasks': {}
}


class Task(object):

    def __init__(self, func, needs=None):
        self.func = func
        self.name = func.__name__
        self.needs = []
        if needs:
            for dep in needs:
                self.add_dependency(dep, append=True)
        env["tasks"][self.name] = self

    def add_dependency(self, dep, append=False):
        task = env["tasks"].get(dep) if isinstance(dep, basestring) else dep
        if not isinstance(task, Task):
            raise Exception('Provided dependency was not found in tasks.')
        if task in self.needs:
            raise Exception('%s already registered as dependency for %s' % \
                (task, self))
        if append:
            self.needs.append(task)
        else:
            self.needs.insert(0, task)

    def __call__(self):
        for dep in self.needs:
            dep()
        self.func()

    def __str__(self):
        return self.name


def task(func):
    if isinstance(func, Task):
        return func
    return Task(func)


def needs(*deps):
    def task(func):
        if isinstance(func, Task):
            for dep in reversed(deps):
                func.add_dependency(dep)
            return func
        else:
            return Task(func, needs=deps)
    return task