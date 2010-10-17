import optparse
import os
import sys

from snake.tasks import Task, FileTask, registry


SNAKEFILE_LOADED = False


def load_snakefile(path, name='snakefile'):
    global SNAKEFILE_LOADED
    if not SNAKEFILE_LOADED:
        sys.path.insert(0, path)
        try:
            imported = __import__(name)
            SNAKEFILE_LOADED = True
        except ImportError:
            print >> sys.stderr, "Error: couldn't find any snakefiles."
            exit(1)
        del sys.path[0]


def find_snakefile():
    path = os.getcwd()
    while True:
        filepath = os.path.join(path, 'snakefile.py')
        if os.path.isfile(filepath):
            load_snakefile(filepath)
            break
        if not os.path.split(path)[1]:
            break
        path = os.path.split(path)[0]


def print_task_list(option, opt_str, value, parser):
    if registry.has_tasks_for(Task):
        print("Task list:")
        for name in sorted(registry.get_tasks_for(Task)):
            print " - %s" % name
    if registry.has_tasks_for(FileTask):
        print("File task list:")
        for name in sorted(registry.has_tasks_for(FileTask)):
            print " - %s" % name
    exit()


def main():
    find_snakefile()
    usage = "%prog [options] [task] ..."
    parser = optparse.OptionParser(usage="%prog [options] [task] ...")
    parser.add_option(
        '-l', '--list', action='callback', callback=print_task_list,
        help="print list of available tasks and exit")
    parser.disable_interspersed_args()
    options, args = parser.parse_args()
    if not args:
        args = ['default']
    for name in args:
        task = registry.get(name, fail_silently=True)
        if not task:
            print >> sys.stderr, "Error: task %r was not found." % name
            exit(1)
        task()
