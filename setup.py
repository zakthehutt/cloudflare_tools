from setuptools import setup
setup(
    name = 'cfscript',
    version = '0.1.0',
    packages = ['cfscript'],
    entry_points = {
        'console_scripts': [
            'cfscript = cfscript.__main__:main'
        ]
    })