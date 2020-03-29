from setuptools import setup, find_packages
import os


def get_version(version_tuple):
    if not isinstance(version_tuple[-1], int):
        return '.'.join(
            map(str, version_tuple[:-1])
        ) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))

init = os.path.join(
    os.path.dirname(__file__), 'cumulativeCurve', '__init__.py'
)

version_line = list(
    filter(lambda l: l.startswith('VERSION'), open(init))
)[0]

VERSION = get_version(eval(version_line.split('=')[-1]))

setup(
    name='cumulativeCurve',
    version=VERSION,
    long_description="""
    cumulativeCurve
    """,
    install_requires=['numpy'],
    packages=find_packages()
)
