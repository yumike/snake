from snake.core import Snake


snake = Snake(__name__)


@snake.task
def clean():
    """remove pyc's and pyo's"""
    snake.sh('find . -name "*.py[co]" -delete')


@snake.task
@depends_on('virtualenv.create')
def develop():
    """create virtualenv and setup Snake into it for development"""
    snake.sh('bin/pip install -e .')


class Virtualenv:

    @snake.task
    def create(self):
        """create virtual environment"""
        snake.sh('virtualenv --no-site-packages --distribute .')

    @snake.task
    def destroy(self):
        """destroy virtual environment"""
        snake.sh('rm -rf bin include lib src')


if __name__ == '__main__':
    snake.run()
