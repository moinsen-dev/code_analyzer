from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="refactoroscope",
    version="0.3.3",
    author="Moinsen Dev",
    author_email="uli@moinsen.dev",
    description="A Python-based command-line tool that provides comprehensive analysis of source code repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moinsen-dev/refactoroscope",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.13",
    install_requires=[
        "rich>=14.1.0",
        "radon>=6.0.1",
        "pygments>=2.19.2",
        "pydantic>=2.11.9",
        "typer>=0.17.4",
        "lizard>=1.17.31",
        "flake8>=7.3.0",
        "pandas>=2.3.2",
        "jinja2>=3.1.6",
        "openpyxl>=3.1.5",
        "pathspec>=0.12.1",
        "pyyaml>=6.0.2",
    ],
    entry_points={
        "console_scripts": [
            "refactoroscope=codeinsight.cli:app",
        ],
    },
)
