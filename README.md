# Code Insight Analyzer

A Python-based command-line tool that provides comprehensive analysis of source code repositories. Think of it as an **MRI scanner for your codebase** - it doesn't just show you what's there, but reveals the health and complexity of your code structure.

## Features

- Scans directories recursively for source code files
- Respects `.gitignore` patterns at all directory levels
- Counts lines of code per file
- Displays file sizes in human-readable format
- Sorts results by line count
- Beautiful terminal output using Rich
- Code complexity analysis (Cyclomatic, Cognitive)
- Export results to JSON/CSV/HTML
- Configuration file support (.codeinsight.yml)

## Installation

First, install [uv](https://github.com/astral-sh/uv) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the dependencies:

```bash
uv sync
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

## Supported Languages

- Python
- JavaScript/TypeScript
- Java
- C#
- C++/C
- Go
- Rust
- Dart/Flutter
- Swift
- Kotlin
- PHP
- Ruby
- HTML/CSS
- SQL
- YAML
- JSON
- Markdown

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