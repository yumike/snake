def depends_on(*tasks):
    def decorator(f):
        f.depends_on = tasks
        return f
    return decorator


def not_a_task(f):
    f.not_a_task = True
    return f
