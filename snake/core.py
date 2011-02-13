import inspect
import imp
import optparse
import os
import subprocess
import sys


class Snake(object):

    usage = "%prog [options] [task] ..."

    def __init__(self, snakefile_name=None):
        self.snakefile_name = snakefile_name
        self.basepath = None
        self.verbosity = 1
        self.called = set()

    def is_task(self, obj):
        return (hasattr(obj, '__module__') and
                obj.__module__ == self.snakefile_name and
                callable(obj) and
                (not hasattr(obj, 'not_a_task') or not obj.not_a_task))

    def is_namespace(self, obj):
        return (hasattr(obj, '__module__') and
                obj.__module__ == self.snakefile_name and
                inspect.isclass(obj) and
                (not hasattr(obj, 'not_a_namespace') or not obj.not_a_namespace))

    def get_ascending_paths(self, path):
        paths = []
        while True:
            paths.append(path)
            path, tail = os.path.split(path)
            if not tail:
                break
        return paths

    def find_snakefile(self):
        paths = self.get_ascending_paths(os.getcwd())
        try:
            return imp.find_module('snakefile', paths)
        except:
            self.abort("couldn't find any snakefile.")

    def get_snakefile(self):
        return imp.load_module('snakefile', *self.find_snakefile())

    def get_snakefile_path(self, snakefile):
        return os.path.dirname(
            os.path.abspath(os.path.expanduser(snakefile.__file__)))

    def get_tasks(self):
        tasks = {}
        namespaces = {}
        for obj_name in dir(self.snakefile_module):
            obj = getattr(self.snakefile_module, obj_name)
            if isinstance(obj, Snake) and obj is not self:
                self.abort("snakefile contains Snake instance which differs "
                           "from used now.")
            if obj_name.startswith('_'):
                continue
            if self.is_namespace(obj):
                namespace = obj()
                namespaces[obj_name.lower()] = obj()
            elif self.is_task(obj):
                tasks[obj_name.lower()] = {'func': obj, 'doc': obj.__doc__}
        for ns_name, namespace in namespaces.items():
            for obj_name in dir(namespace):
                if obj_name.startswith('_'):
                    continue
                obj = getattr(namespace, obj_name)
                if self.is_task(obj):
                    task_name = '%s.%s' % (ns_name, obj_name.lower())
                    tasks[task_name] = {'func': obj, 'doc': obj.__doc__}
        return tasks

    def init_snakefile(self):
        if self.snakefile_name is None:
            self.snakefile_module = self.get_snakefile()
            self.snakefile_name = self.snakefile_module.__name__
        else:
            self.snakefile_module = sys.modules[self.snakefile_name]
        self.snakefile_path = self.get_snakefile_path(self.snakefile_module)
        self.tasks = self.get_tasks()
        self.notice("(in %s)" % self.snakefile_path)

    def get_parser(self):
        parser = optparse.OptionParser(usage=self.usage)
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
        self.init_snakefile()
        tasks = {}
        for name, info in self.tasks.items():
            if info['doc']:
                tasks[name] = info['doc']
        if tasks:
            max_length = max(len(name) for name in tasks)
            for name in sorted(tasks):
                doc = tasks[name]
                if doc:
                    print('%s  # %s ' % (name.ljust(max_length), doc))
        exit()

    def run_task(self, name):
        if name in self.called:
            return
        self.called.add(name)
        task = self.tasks[name]['func']
        if hasattr(task, 'depends_on'):
            for dep in task.depends_on:
                self.run_task(dep)
        task()

    def run(self):
        parser = self.get_parser()
        options, args = parser.parse_args()
        if options.verbose:
            self.verbosity += 1
        if options.quiet:
            self.verbosity -= 1
        self.init_snakefile()
        for name in args:
            self.run_task(name)

    def info(self, msg):
        if self.verbosity > 1:
            print(msg)

    def notice(self, msg):
        if self.verbosity > 0:
            print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print >> sys.stderr, "Error: %s" % msg

    def abort(self, msg):
        self.error(msg)
        sys.exit(1)

    def sh(self, command, cwd=False, capture=False):
        kwargs = {'shell': True}
        if capture:
            kwargs['stdout'] = subprocess.PIPE
        self.notice("[sh] %s" % command)
        if not cwd:
            path = self.snakefile_path.replace(' ', '\ ')
            command = 'cd %s && %s' % (path, command)
        return subprocess.Popen([command], **kwargs).communicate()[0]


snake = Snake()
