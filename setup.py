"""Setup configuration for Echo package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="echo-ai-architect",
    version="0.1.0",
    author="Nathan Poinsette",
    author_email="",
    description="Self-Evolving AI Architect - Recursive problem-solving engine with economic opportunity detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onlyecho822-source/Echo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "echo=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json"],
    },
)
