# Code Insight Analyzer

[![Build Status](https://github.com/moinsen-dev/code-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/moinsen-dev/code-analyzer/actions)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/moinsen-dev/code-analyzer)](LICENSE)
[![Code Coverage](https://img.shields.io/codecov/c/github/moinsen-dev/code-analyzer)](https://codecov.io/gh/moinsen-dev/code-analyzer)
[![PyPI version](https://badge.fury.io/py/codeinsight.svg)](https://badge.fury.io/py/codeinsight)

![Code Analyzer Icon](code-analyzer-icon.png)

A Python-based command-line tool that provides comprehensive analysis of source code repositories. Think of it as an **MRI scanner for your codebase** - it doesn't just show you what's there, but reveals the health and complexity of your code structure.

![Code Analyzer Wallpaper](code-analyzer-wallpaper.png)

## Features

- Scans directories recursively for source code files
- Respects `.gitignore` patterns at all directory levels
- Counts lines of code per file
- Displays file sizes in human-readable format
- Sorts results by line count
- Beautiful terminal output using Rich
- Code complexity analysis (Cyclomatic, Cognitive, Halstead)
- Duplicate code detection using AST-based analysis
- Export results to JSON/CSV/HTML
- Configuration file support (.codeinsight.yml)
- Multi-language support (60+ programming languages)
- Performance optimizations with parallel processing

## Installation

First, install [uv](https://github.com/astral-sh/uv) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the dependencies:

```bash
uv sync
```

Or install directly from PyPI:

```bash
pip install codeinsight
```

## Usage

### Basic Analysis

```bash
# Analyze current directory
uv run codeinsight analyze .

# Analyze specific directory
uv run codeinsight analyze /path/to/project

# Include complexity analysis
uv run codeinsight analyze . --complexity
```

### Output Formats

```bash
# Display in terminal (default)
uv run codeinsight analyze . --output terminal

# Export to JSON
uv run codeinsight analyze . --export json --export-dir ./reports

# Export to multiple formats
uv run codeinsight analyze . --export json,html --export-dir ./reports
```

### Advanced Usage

```bash
# Compare two analysis reports
uv run codeinsight compare reports/report1.json reports/report2.json

# Initialize configuration file
uv run codeinsight init
```

## Supported Languages

The Code Insight Analyzer supports 60+ programming languages:

- **Primary**: Python, JavaScript/TypeScript, Java, C#, C++/C, Go, Rust
- **Mobile**: Dart/Flutter, Swift, Kotlin
- **Web**: HTML, CSS/SCSS, Vue, React, Svelte
- **Scripting**: PHP, Ruby
- **Configuration**: YAML, JSON, TOML, XML
- **Data**: SQL, GraphQL
- **Documentation**: Markdown, reStructuredText

## Configuration

Create a `.codeinsight.yml` file in your project root:

```yaml
version: 1.0

# Language-specific settings
languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15

# Analysis rules
analysis:
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"

  complexity:
    include_docstrings: false
    count_assertions: true

  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

# Output preferences
output:
  format: "terminal"  # terminal, json, html, csv
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
```

## Documentation

For detailed documentation, visit our [GitHub Pages site](https://moinsen-dev.github.io/code-analyzer/).

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for more information.

## Release Process

New versions are automatically published to PyPI when a new tag is created following the pattern `v*.*.*`. To release a new version:

1. Update the version in `pyproject.toml` and `setup.py`
2. Create a new tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
3. Push the tag: `git push origin v1.0.0`
4. The GitHub Actions workflow will automatically build and publish to PyPI