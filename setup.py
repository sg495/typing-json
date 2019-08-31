""" setup.py created according to https://packaging.python.org/tutorials/packaging-projects """

import setuptools #type:ignore

with open("README.md", "r") as fh:
    long_description: str = fh.read()

setuptools.setup(
    name="typing-json",
    version="0.0.1",
    author="sg495",
    author_email="sg495@users.noreply.github.com",
    description="Add typing support to python JSON serialization.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sg495/typing-json",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
