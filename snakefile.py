from snake.core import Snake
from snake.helpers import depends_on


snake = Snake(__name__)
sh = snake.sh


def clean():
    """remove pyc's and pyo's"""
    sh('find . -name "*.py[co]" -delete')


@depends_on('virtualenv.create')
def develop():
    """create virtualenv and setup Snake into it for development"""
    sh('bin/pip install -e .')


class Virtualenv:

    def create(self):
        """create virtual environment"""
        sh('virtualenv --no-site-packages --distribute .')

    def destroy(self):
        """destroy virtual environment"""
        sh('rm -rf bin include lib src')


if __name__ == '__main__':
    snake.run()
