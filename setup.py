from setuptools import setup, find_packages
import os

# 读取版本号
def read_version():
    version_file = os.path.join('pyfmm-gui', '_version.py')
    with open(version_file) as f:
        exec(f.read())
    return locals()['__version__']

setup(
    name='pyfmm-gui',
    version=read_version(),
    description='A simple GUI of PyFMM',
    author='Zhu Dengda',
    author_email='zhudengda@mail.iggcas.ac.cn',
    packages=find_packages(),
    package_data={'pyfmm-gui': ['main.ui']},
    include_package_data=True,
    python_requires='>=3.9',
)
