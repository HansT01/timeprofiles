from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.2"
DESCRIPTION = "Easily profile time taken for methods to complete."

# Setting up
setup(
    name="timeprofiles",
    version=VERSION,
    url="https://github.com/HansT01/timeprofiles",
    author="Hans Teh",
    author_email="<hansteh001@gmail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=find_packages(),
    install_requires=["numpy", "matplotlib", "tabulate"],
    keywords=["python", "time", "profile", "class", "method"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    test_suite="tests",
)
