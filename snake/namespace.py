class Namespace(dict):

    def __init__(self, name, snake, prefix=None):
        self.name = name
        self.snake = snake
        if prefix:
            self.path = ':'.join([prefix, name])
        else:
            self.path = name

    def add(self, item):
        self[item.name.split(':')[-1]] = item

    def find(self, path, fail_silently=False):
        name = path[0]
        if name not in self:
            if fail_silently:
                return
            raise Exception("%r not found" % name)
        item = self[name]
        if len(path) == 1:
            return item
        if isinstance(item, Namespace):
            return item.find(path[1:])
        if not fail_silently:
            raise Exception("%r too long path" % name)

    def resolve(self, name, cls=None, create=False, fail_silently=False):
        if name not in self and cls and create:
            if self.path:
                name = ':'.join([self.path, name])
            item = cls(name, self.snake)
            self.add(item)
            return item
        if name not in self:
            if fail_silently:
                return
            raise Exception("%r not found" % name)
        item = self[name]
        if cls and not isinstance(name, cls):
            if fail_silently:
                return
            raise Exception("%s %r not found." % (cls.__name__, name))
        return item
