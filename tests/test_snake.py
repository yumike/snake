from nose.tools import with_setup
from snake.core import Snake


snake = Snake()


@snake.task
def configure():
    pass


@snake.task
def build():
    pass


@snake.task
@snake.depends_on('configure', 'build')
def install():
    """Configure, build and install project"""


def setup_func():
    pass


def teardown_func():
    snake.called = set()


reset_snake = with_setup(setup_func, teardown_func)


def test_snake_defaults():
    snake = Snake()
    assert snake.called == set()
    assert snake.current_namespace == ''
    assert snake.tasks == {}
    assert snake.verbosity == 1


def test_registered_tasks():
    assert set(snake.tasks.keys()) == set(['configure', 'build', 'install'])

    for func in (configure, build, install):
        assert snake.tasks[func.__name__]['func'] is func

    assert snake.tasks['configure']['doc'] is None
    assert snake.tasks['install']['doc'] == "Configure, build and install project"


def test_stored_dependencies():
    assert install.depends_on == ('configure', 'build')


def test_task_overriding():
    snake = Snake()

    @snake.task
    @snake.depends_on('this')
    def task():
        """One description"""

    old_task = task

    @snake.task
    @snake.depends_on('that')
    def task():
        """Other description"""

    assert task is not old_task
    assert snake.tasks['task']['func'] is task
    assert snake.tasks['task']['doc'] == "Other description"


@reset_snake
def test_run_task():
    snake.run_task('build')
    assert snake.called == set(['build'])


@reset_snake
def test_run_task_with_dependencies():
    snake.run_task('install')
    assert snake.called == set(['configure', 'build', 'install'])


def test_run_snake():
    snake.run(['configure', 'build', 'install'])
    assert snake.called == set(['configure', 'build', 'install'])
