=====
Snake
=====

Snake is yet another Make-like tool, written on Python and inspired by Rake.


Usage Example
=============

In a directory with ``snakefile.py`` (or in any sub-directory) containing such code::

    from snake import depends_on, sh

    @depends_on('virtualenv', 'install')
    def init():
        print("Activate your virtualenv with:")
        print("  $ source bin/activate")

    def virtualenv():
        sh('virtualenv -q --no-site-packages .')

    def install():
        sh('bin/pip -q install -e .')

run::

    $ snake init
    (in /Users/yumike/Projects/Snake)
    [sh] virtualenv -q --no-site-packages .
    [sh] bin/pip -q install -e .
    Activate your virtualenv with:
      $ source bin/activate
