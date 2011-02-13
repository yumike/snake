import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name = 'Snake',
    version = '0.2',
    url = 'http://yumatov.org/snake/',
    description = 'Snake is yet another Make-like tool inspired by Rake.',
    long_description = read('README.rst'),
    author = 'Mike Yumatov',
    author_email = 'mike@yumatov.org',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'snake = snake.core:snake.run',
        ]
    },
)
