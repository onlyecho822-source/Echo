"""
Setup configuration for WiFi Scanner and Decoder package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="wifi-scanner",
    version="1.0.0",
    author="Echo Civilization",
    author_email="echo@example.com",
    description="Cross-platform WiFi network scanner and decoder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/echo-civilization/wifi-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "rich": [
            "rich>=13.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wifi-scanner=wifi_scanner.cli:main",
            "wifi-scan=wifi_scanner.cli:main",
        ],
    },
    keywords=[
        "wifi",
        "wireless",
        "network",
        "scanner",
        "decoder",
        "analyzer",
        "802.11",
    ],
    project_urls={
        "Bug Reports": "https://github.com/echo-civilization/wifi-scanner/issues",
        "Source": "https://github.com/echo-civilization/wifi-scanner",
    },
)
