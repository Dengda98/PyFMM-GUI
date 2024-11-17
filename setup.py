from setuptools import setup, find_packages
import os

# 读取版本号
def read_version():
    version_file = os.path.join('pyfmm_gui', '_version.py')
    with open(version_file) as f:
        exec(f.read())
    return locals()['__version__']

def read_readme():
    with open("README.md", encoding="utf-8") as f:
        return f.read()

setup(
    name='pyfmm_gui',
    version=read_version(),
    description='A simple GUI of PyFMM',
    author='Zhu Dengda',
    author_email='zhudengda@mail.iggcas.ac.cn',
    long_description=read_readme(),  
    long_description_content_type="text/markdown", 
    url="https://github.com/Dengda98/PyFMM-GUI",

    packages=find_packages(),
    package_data={'pyfmm_gui': ['main.ui']},
    include_package_data=True,
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'pyfmm_gui=pyfmm_gui.main:main', 
            'pyfmm-gui=pyfmm_gui.main:main', 
        ],
    },
)
