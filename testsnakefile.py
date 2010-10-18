from snake.api import *


@filetask('README.html', needs='README.rst')
def _(t):
    sh('rst2html.py README.rst > README.html')

@task
def clean():
    sh('rm README.html')
    sh('find . -name "*.pyc" -delete')
    sh('find . -name "*.pyo" -delete')

@task
def configure(t):
    info(t.name)

task('build').needs('README.html')

@task
def install():
    debug('install')

task('default').needs(clean, configure, 'build')
task('default').also_needs(install)
