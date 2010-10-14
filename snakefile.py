from snake.api import *


@task
def clean():
    sh("find . -name '*.pyc' -delete")
    sh("find . -name '*.pyo' -delete")

@task
def configure():
    print 'configure'

@task
def build():
    print 'build'

@task
def install():
    print 'install'

task('default', deps=(clean, configure, build, install))
