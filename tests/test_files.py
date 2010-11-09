from __future__ import with_statement

import os
import time

from contextlib import contextmanager
from snake.api import *
from tempfile import NamedTemporaryFile


@contextmanager
def tempfilename(content=None):
    f = NamedTemporaryFile(delete=False)
    name = f.name
    f.write(content or "Hello world!")
    f.close()
    yield name
    os.remove(name)


def test_file():
    snake = Snake()
    with tempfilename() as source:
        time.sleep(1)
        with tempfilename() as prerequisite:
            @snake.file(source, depends_on=prerequisite)
            def _(t):
                t.called = True
            task = snake.find(source)
            task.called = False
            task()
            assert task.called
