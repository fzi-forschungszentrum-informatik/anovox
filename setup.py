"""
This Python code is for a setup.py file, which is used to distribute Python packages.
Run the following command to install the package:
    python setup.py install or pip install .
"""
from distutils.core import setup

PROJECT_NAME = "Januar"
VERSION = "1.0"
PROJECT_URL = "xxx"
AUTHOR_NAME = "xxx"
AUTHOR_EMAIL = "xxx"
DESCRIPTION = "AnoVox"
LICENSE = "MIT"
PACKAGES = [
    "Models",
    "Models.World",
    "Scenarios",
    "DataAnalysis",
]

setup(
    name=PROJECT_NAME,
    version=VERSION,
    packages=PACKAGES,
    url=PROJECT_URL,
    license=LICENSE,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
)
