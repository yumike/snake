def depends_on(*tasks):
    def decorator(f):
        f.depends_on = tasks
        return f
    return decorator


def task(f):
    f.task = True
    return f
