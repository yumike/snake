from snake import App, Snake


snake = Snake()


@snake.task
def clean():
    """remove pyc's and pyo's"""
    snake.sh('find . -name "*.py[co]" -delete')


@snake.task
@snake.depends_on('virtualenv.create')
def develop():
    """create virtualenv and setup Snake into it for development"""
    snake.sh('bin/pip install -e .')


with snake.namespace('virtualenv'):
    @snake.task
    def create():
        """create virtual environment"""
        snake.sh('virtualenv --no-site-packages --distribute .')

    @snake.task
    def destroy():
        """destroy virtual environment"""
        snake.sh('rm -rf bin include lib src')


if __name__ == '__main__':
    App(__name__).run()
