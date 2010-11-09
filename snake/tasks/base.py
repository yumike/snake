import inspect


class BaseTask(object):

    def __init__(self, name, snake, prerequisites=None, func=None):
        self.name = name
        self.snake = snake
        self.func = func
        self.prerequisites = []
        if prerequisites:
            self.depends_on(*prerequisites)

    def __call__(self):
        raise NotImplementedError

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

    def depends_on(self, *tasks, **kwargs):
        if kwargs.get('replace', False):
            self.prerequisites = []
        self.prerequisites.extend(self._prepare_prerequisites(tasks))
        return self

    def calls(self, func):
        self.func = func
        return self

    def call(self):
        if self.func:
            if inspect.getargspec(self.func)[0]:
                self.func(self)
            else:
                self.func()
