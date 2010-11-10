from snake.api import *


@file("README.html")
def _(t):
    sh("touch README.html")


@task
def clean():
    sh('rm README.html')
    sh('find . -name "*.pyc" -delete')
    sh('find . -name "*.pyo" -delete')


@task
def configure(t):
    info(t.name)


@task
def install():
    warning('install')


task('build').depends_on('README.html')
task('default').depends_on(clean, configure, 'build', install)


with namespace('users'):
    @command(takes=[
        ('name', 'set user name'),
    ])
    def create(c, options, args):
        print options, args


if __name__ == '__main__':
    snake.run(__file__)
