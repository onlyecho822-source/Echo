"""
Hydra - Multi-AI Fusion Cybersecurity System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hydra-cybersec",
    version="0.1.0",
    author="Echo Project",
    author_email="onlyecho822@gmail.com",
    description="Multi-AI Fusion Cybersecurity Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onlyecho822-source/Echo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "asyncio-mqtt>=0.16.0",
        "aiohttp>=3.8.0",
        "httpx>=0.27.0",
        "flask>=3.0.0",
        "flask-socketio>=5.3.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "claude": ["anthropic>=0.18.0"],
        "openai": ["openai>=1.12.0"],
        "gemini": ["google-generativeai>=0.4.0"],
        "all": [
            "anthropic>=0.18.0",
            "openai>=1.12.0",
            "google-generativeai>=0.4.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=24.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hydra=hydra.main:main",
        ],
    },
)
