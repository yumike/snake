from snake import *


@task
def clean():
    """remove pyc's and pyo's"""
    sh('find . -name "*.py[co]" -delete')
