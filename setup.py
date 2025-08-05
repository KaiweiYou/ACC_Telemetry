from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="acc_telemetry",
    version="1.0.0",
    author="Ryan Rennoir",
    author_email="ryanrennoir9@gmail.com",
    url="https://github.com/rrennoir/PyAccSharedMemory",
    description="Assetto Corsa Competizione telemetry data reader and visualization tool",
    packages=find_packages(),
    install_requires=[
        "python-osc>=1.8.0",
        "typing>=3.7.4",
        "dataclasses>=0.8",
    ],
    entry_points={
        "console_scripts": [
            "acc-telemetry=main:main",
        ],
    },
    classifiers=[
        "Operating System :: Microsoft",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)