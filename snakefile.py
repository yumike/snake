from snake.core import Snake
from snake.helpers import depends_on, task


snake = Snake(__name__)
sh = snake.sh


@task
def clean():
    """remove pyc's and pyo's"""
    sh('find . -name "*.py[co]" -delete')


@task
@depends_on('virtualenv.create')
def develop():
    """create virtualenv and setup Snake into it for development"""
    sh('bin/pip install -e .')


class Virtualenv:

    @task
    def create(self):
        """create virtual environment"""
        sh('virtualenv --no-site-packages --distribute .')

    @task
    def destroy(self):
        """destroy virtual environment"""
        sh('rm -rf bin include lib src')


if __name__ == '__main__':
    snake.run()
