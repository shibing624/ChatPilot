# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages

# Avoids IDE errors, but actual version is read from version.py
__version__ = ""
exec(open('chatpilot/version.py').read())

if sys.version_info < (3,):
    sys.exit('Sorry, Python3 is required.')

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='chatpilot',
    version=__version__,
    description='Chat Agent toolkit.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='XuMing',
    author_email='xuming624@qq.com',
    url='https://github.com/shibing624/chatpilot',
    license="Apache License 2.0",
    zip_safe=False,
    python_requires=">=3.9.0",
    entry_points={"console_scripts": ["chatpilot = chatpilot.cli:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords='llm,agent',
    install_requires=[
        "loguru",
        "tiktoken",
        "langchain~=0.1.11",
        "langchain-community~=0.0.27",
        "langchain-openai~=0.0.8",
        "openai~=1.13.3",
    ],
    packages=find_packages(exclude=['tests']),
    package_dir={'chatpilot': 'chatpilot'},
    package_data={'chatpilot': ['*.*', 'data/*.txt']}
)
