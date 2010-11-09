from snake.api import *


def test_global_namespace():
    snake = Snake()
    configure = snake.task('configure')
    make = snake.task('make')
    test = snake.task('test')
    assert sorted(snake.tasks) == ['configure', 'make', 'test']
    assert snake.tasks['make'] is make

def test_namespaced_tasks():
    snake = Snake()
    with snake.namespace('docs'):
        make = snake.task('make')
    default = snake.task('default', depends_on=make)
    assert make.name == 'docs:make', "%r != 'docs:make'" % make.name
    assert snake.find('docs:make') is make
    assert 'docs:make' in default.prerequisites

def test_nested_namespaces():
    snake = Snake()
    with snake.namespace('app'):
        with snake.namespace('docs'):
            make = snake.task('make')
    assert snake.find('app:docs:make') is make

def test_namespace_default_task():
    snake = Snake()
    with snake.namespace('docs'):
        default = snake.task('default')
    assert snake.find('docs') is default
