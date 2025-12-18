#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for git_data_graph."""

from setuptools import setup, find_packages
import os

# Read version from package
here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, "src", "__init__.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, about)
            break

# Read long description from README if it exists
long_description = ""
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="git_data_graph",
    version=about.get("__version__", "0.1.0"),
    description="A tool to visualize Git repository internals for educational purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="git_data_graph contributors",
    python_requires=">=3.6",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_dir={"": "."},
    py_modules=["src"],
    entry_points={
        "console_scripts": [
            "git_data_graph=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    keywords="git visualization education graph",
)
