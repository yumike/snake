from snake.api import *


@task
def clean():
    print 'clean'

@task(deps=clean)
def configure():
    print 'configure'

@task(deps=configure)
def build():
    print 'build'

@task(deps=build)
def install():
    print 'install'

task('default', deps='install')