import os
from snake.tasks.base import BaseTask


class File(BaseTask):

    def _is_outdated(self):
        return (not os.path.exists(self.name) or self.prerequisites and (
            os.stat(self.name).st_mtime < max(
                os.stat(prerequisite).st_mtime
                for prerequisite in self.prerequisites)))

    def __call__(self):
        if self.name not in self.snake.called:
            self.snake.called.add(self.name)
            for prerequisite in self.prerequisites:
                if prerequisite in self.snake.files:
                    self.snake.files[prerequisite]()
                elif not os.path.exists(prerequisite):
                    raise Exception("File %r does not exists" % prerequisite)
            if self._is_outdated():
                self.call()
