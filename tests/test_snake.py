from nose.tools import with_setup
from snake.core import Snake


snake = Snake()
log = []


@snake.task
def configure():
    log.append('configure')


@snake.task
def build():
    log.append('build')


@snake.task
@snake.depends_on('configure', 'build')
def install():
    """Configure, build and install project"""
    log.append('install')


def teardown_func():
    log[:] = []
    snake.called = set()


reset_snake = with_setup(teardown=teardown_func)


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
    assert log == ['build']


@reset_snake
def test_run_task_with_dependencies():
    snake.run_task('install')
    assert snake.called == set(['configure', 'build', 'install'])


@reset_snake
def test_run_snake():
    snake.run(['install'])
    assert snake.called == set(['configure', 'build', 'install'])


@reset_snake
def test_task_called_once():
    snake.run(['configure', 'configure'])
    assert log == ['configure']
