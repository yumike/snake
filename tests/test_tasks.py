from snake.api import *


def test_task_name():
    snake = Snake()
    @snake.task
    def configure():
        pass
    assert configure.name == 'configure'

def test_prerequisites():
    snake = Snake()
    configure = snake.task('configure')
    make = snake.task('make')
    test = snake.task('test')
    default = snake.task('default', depends_on=[configure, make, test])
    assert default.prerequisites == ['configure', 'make', 'test']

def test_call():
    snake = Snake()
    snake.foo = ''
    @snake.task
    def make():
        snake.foo = 'bar'
    make()
    assert snake.foo == 'bar'

def test_call_with_task():
    snake = Snake()
    @snake.task
    def make(t):
        t.foo = 'bar'
    make.foo = ''
    make()
    assert make.foo == 'bar'

def test_call_twice():
    snake = Snake()
    @snake.task
    def make(t):
        t.count += 1
    make.count = 0
    make()
    make()
    assert make.count == 1

def test_inherited_prerequisites():
    snake = Snake()
    snake.call_order = []
    def append(t):
        t.snake.call_order.append(t.name)
    clean = snake.task('clean').calls(append)
    configure = snake.task('configure').depends_on(clean).calls(append)
    make = snake.task('make').depends_on(clean).calls(append)
    default = snake.task('default').depends_on(configure, make)
    default()
    assert snake.call_order == ['clean', 'configure', 'make']

def test_task_override():
    snake = Snake()
    old_make = snake.task('make')
    @snake.task
    def make():
        pass
    assert make is not old_make
