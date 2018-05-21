from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='web-python-2018-04-ht06-orm',
    version='1.0',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        # 'uwsgi',
        # 'jinja2',
        'pysqlite3',
        'nose'
    ],
    entry_points={
    },
    test_suite='nose.collector',
    tests_require=[
        'nose',
    ],
)
