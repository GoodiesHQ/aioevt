#!/usr/bin/env python3

import setuptools


setuptools.setup(
    name="aioevt",
    version="2.2.1",
    author="Austin Archer",
    author_email="aarcher@protonmail.com",
    long_description=open("README.md", "r").read(),
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
