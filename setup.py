#!/usr/bin/env python3

import setuptools

from aioevt import __version__ as aioevt_version
from aioevt import __author__ as aioevt_author


with open("README.md", "r") as fin:
    long_description = fin.read()


setuptools.setup(
    name="aioevt",
    version=aioevt_version,
    author=aioevt_author,
    author_email="aarcher@protonmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GoodiesHQ/aioevt",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
)
