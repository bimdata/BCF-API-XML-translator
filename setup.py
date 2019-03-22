import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="bcf_api_xml",
    version="0.1.9",
    description="Convert BCF-API to BCF-XML",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bimdata/BCF-API-XML",
    author="Hugo Duroux",
    author_email="hugo@bimdata.io",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["lxml"],
)
