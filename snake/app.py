import os
import sys
from imp import find_module, load_module
from optparse import OptionParser

from .core import Snake


class App(object):

    usage = "%prog [options] [task] ..."

    def __init__(self, snakefile_name=None):
        self.snakefile_module = self.get_snakefile_module(snakefile_name)
        self.snake = self.find_snake(self.snakefile_module)
        self.snakefile_dirname = self.get_snakefile_dirname(self.snakefile_module)

    def get_snakefile_module(self, snakefile_name=None):
        if snakefile_name:
            return sys.modules[snakefile_name]
        return load_module('snakefile', *self.find_snakefile_module())

    def find_snake(self, snakefile_module):
        for name in dir(snakefile_module):
            attr = getattr(snakefile_module, name)
            if isinstance(attr, Snake):
                return attr
        filename = snakefile_module.__file__
        self.abort("couldn't find any Snake instance in %r." % filename)

    def get_snakefile_dirname(self, snakefile_module):
        snakefile_path = os.path.expanduser(snakefile_module.__file__)
        return os.path.dirname(os.path.abspath(snakefile_path))

    def find_snakefile_module(self):
        paths = self.get_ascending_paths(os.getcwd())
        try:
            return find_module('snakefile', paths)
        except:
            self.abort("couldn't find any snakefile.")

    def get_ascending_paths(self, path):
        paths = []
        while True:
            paths.append(path)
            path, tail = os.path.split(path)
            if not tail:
                break
        return paths

    def get_parser(self):
        parser = OptionParser(usage=self.usage)
        parser.disable_interspersed_args()
        parser.add_option('-v', '--verbose', action='store_true',
                          dest='verbose', default=False,
                          help="give more output")
        parser.add_option('-q', '--quiet', action='store_true', dest='quiet',
                          default=False, help="give less output")
        parser.add_option('-l', '--list', action='callback',
                          callback=self.print_task_list,
                          help="print task list end exit")
        return parser

    def print_task_list(self, option, opt_str, value, parser):
        tasks = {}
        for name, info in self.snake.tasks.items():
            if info['doc']:
                tasks[name] = info['doc']
        if tasks:
            max_length = max(len(name) for name in tasks)
            for name in sorted(tasks):
                doc = tasks[name]
                if doc:
                    print('%s  # %s ' % (name.ljust(max_length), doc))
        exit()

    def run(self):
        os.chdir(self.snakefile_dirname)
        print("(in %s)" % self.snakefile_dirname)
        parser = self.get_parser()
        options, args = parser.parse_args()
        if options.verbose:
            self.snake.verbosity += 1
        if options.quiet:
            self.snake.verbosity -= 1
        self.snake.run(args)

    def abort(self, msg):
        print >> sys.stderr, "Error: %s" % msg
        sys.exit(1)


def run():
    App().run()
