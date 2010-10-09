from setuptools import setup, find_packages


setup(
    name = 'Snake',
    version = '0.1dev',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'snake = snake.main:main',
        ]
    }
)