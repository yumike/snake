from .app import App
from .core import Snake


__all__ = ['snake', 'depends_on', 'namespace', 'sh', 'task']


snake = Snake()
depends_on = snake.depends_on
namespace = snake.namespace
sh = snake.sh
task = snake.task
