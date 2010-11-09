from snake.api import *
from snake.namespaces import Namespace


def test_snake():
    snake = Snake()
    assert isinstance(snake.tasks, Namespace)
    assert snake.tasks.name == ''
    assert snake.tasks is snake.current_namespace
