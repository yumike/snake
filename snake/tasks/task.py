from snake.tasks.base import BaseTask


class Task(BaseTask):

    def __call__(self):
        if self.name not in self.snake.called:
            self.snake.called.add(self.name)
            for prerequisite in self.prerequisites:
                self.snake.find(prerequisite)()
            self.call()
