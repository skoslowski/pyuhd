import re
from setuptools import setup, find_packages

with open('pyuhd/__init__.py') as init_file:
    package_docstring = init_file.readline().strip('"\n')
    package_info = {
        m.group(1): m.group(2)
        for m in re.finditer(r"__(.*?)__ ?= ?'([^']*?)'", init_file.read())
    }


setup(
    name='pyuhd',
    version=package_info['version'],
    packages=find_packages(exclude=['tests']),

    setup_requires=[
        'cffi >= 1.0.0',
        # 'setuptools_git >= 0.3',
    ],

    install_requires=['cffi>=1.0.0'],
    cffi_modules=['pyuhd/uhd_build.py:ffibuilder'],

    author=package_info['author'],
    author_email=package_info['email'],
    license=package_info['license'],
    description=package_docstring,

)

