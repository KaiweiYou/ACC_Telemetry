# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取生产环境依赖
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

# 读取开发环境依赖（如果文件存在）
development_requirements = []
if os.path.exists("dev-requirements.txt"):
    with open("dev-requirements.txt", "r", encoding="utf-8") as fh:
        development_requirements = [
            line.strip()
            for line in fh
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ]

setup(
    name="acc-telemetry",
    version="1.0.0",
    author="KaiweiYou",
    author_email="youkaiwei5@gmail.com",
    url="https://github.com/KaiweiYou/ACC_Telemetry",
    description="Assetto Corsa Competizione telemetry data reader and visualization tool with GUI",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": development_requirements,
    },
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
        "License :: OSI Approved :: MIT License",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)
