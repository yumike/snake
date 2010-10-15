from snake.api import *


@filetask('README.html', deps='README.rst')
def _(t):
    sh('rst2html.py README.rst > README.html')


@task
def clean():
    sh("rm README.html")
    sh("find . -name '*.pyc' -delete")
    sh("find . -name '*.pyo' -delete")

@task
def configure():
    print 'configure'

task('build', deps='README.html')

@task
def install():
    print 'install'

task('default', deps=(clean, configure, 'build', install))
