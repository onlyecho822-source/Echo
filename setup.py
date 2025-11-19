"""Setup configuration for Echo Reverse Engineering Engine."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="echo-engine",
    version="0.1.0",
    author="Echo Civilization",
    author_email="onlyecho822@gmail.com",
    description="A reverse engineering engine for tracing information to its origins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onlyecho822-source/Echo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: General",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Core dependencies (all stdlib for now)
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "ruff>=0.1",
            "mypy>=1.0",
        ],
        "web": [
            "requests>=2.28",
            "beautifulsoup4>=4.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "echo-engine=echo_engine.cli:main",
        ],
    },
    keywords=[
        "reverse-engineering",
        "fact-checking",
        "source-tracing",
        "provenance",
        "investigation",
        "analysis",
    ],
)
