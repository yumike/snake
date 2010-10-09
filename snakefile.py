from snake.api import *


@task
def clean():
    print(" - clean")


@task
def build():
    print(" - build")


@task
def install():
    print(" - install")


@task
def configure():
    print(" - configure")


@task
@needs(clean, configure)
@needs(build, install)
def default():
    print(" - default")