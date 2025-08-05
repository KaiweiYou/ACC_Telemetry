from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="acc-telemetry",
    version="1.0.0",
    author="Ryan Rennoir",
    author_email="ryanrennoir9@gmail.com",
    url="https://github.com/rrennoir/PyAccSharedMemory",
    description="Assetto Corsa Competizione telemetry data reader and visualization tool with GUI",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "acc-telemetry=main:main",
        ],
    },
    classifiers=[
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8"
)