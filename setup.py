#!/usr/bin/env python3

import re

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version():
    with open("captchaly/__init__.py", "r") as f:
        version = re.search(r'__version__ = ["\'](.*?)["\']', f.read())
        if version is None:
            return "Error getting version."

        return version.group(1)


setup(
    name="captchaly",
    version=get_version(),
    description="Captchaly's CAPTCHAs solving service API for Python. Unofficial.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heav33n/captchaly-python/",
    install_requires=["requests"],
    author="heav33n",
    author_email="support@captchaly.com",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    test_suite="tests",
)
