"""
Echo Nexus Python SDK Setup
"""

from setuptools import setup, find_packages

setup(
    name="echo-nexus",
    version="0.1.0",
    description="Echo Nexus - Distributed Intelligence Platform",
    author="Nathan Poinsette",
    author_email="nathan@echonexus.dev",
    url="https://github.com/onlyecho822-source/Echo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "cryptography>=41.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "echo-nexus=echo_nexus.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
