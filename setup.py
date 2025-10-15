#!/usr/bin/env python3
"""
Setup script for ScriptAI
Enterprise-Grade AI-Powered Code Generation Platform
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


setup(
    name="scriptai",
    version="1.2.0",
    author="ScriptAI Team",
    author_email="team@scriptai.dev",
    description="Enterprise-Grade AI-Powered Code Generation Platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/qtaura/ScriptAI",
    project_urls={
        "Bug Reports": "https://github.com/qtaura/ScriptAI/issues",
        "Source": "https://github.com/qtaura/ScriptAI",
        "Documentation": "https://github.com/qtaura/ScriptAI#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pytest-cov>=4.0.0",
            "bandit>=1.7.0",
            "safety>=2.0.0",
            "pre-commit>=2.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "scriptai=cli:main",
        ],
        "gui_scripts": [
            "scriptai-gui=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.svg"],
    },
    zip_safe=False,
    keywords="ai code-generation openai huggingface cli web",
)
