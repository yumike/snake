from snake.api import *


@task
def clean():
    print(" - clean")


@task
def build():
    print(" - build")


@task(deps=clean)
def install():
    print(" - install")


@task
def configure():
    print(" - configure")


@task(deps=(build, install))
def default():
    print(" - default")


default.deps.add(clean, configure)
task('build').deps.add('clean')