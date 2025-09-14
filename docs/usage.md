---
layout: default
title: Usage Guide
---

# Usage Guide

## Basic Analysis

### Analyzing a Directory

To analyze the current directory:

```bash
uv run code_analyzer analyze .
```

To analyze a specific directory:

```bash
uv run code_analyzer analyze /path/to/project
```

### Including Complexity Analysis

To include detailed complexity metrics:

```bash
uv run code_analyzer analyze . --complexity
```

## Output Formats

### Terminal Output (Default)

```bash
uv run code_analyzer analyze . --output terminal
```

### Exporting Results

Export to JSON:

```bash
uv run code_analyzer analyze . --export json --export-dir ./reports
```

Export to multiple formats:

```bash
uv run code_analyzer analyze . --export json,html --export-dir ./reports
```

## Command Line Options

### Main Commands

- `analyze`: Analyze a codebase
- `compare`: Compare two analysis reports
- `init`: Initialize a configuration file

### Analyze Options

- `--complexity` or `-c`: Include complexity analysis
- `--output` or `-o`: Output format (terminal, json, html, csv)
- `--export` or `-e`: Export formats (json, html, csv)
- `--export-dir`: Directory for exports
- `--top-files` or `-t`: Number of top files to display

### Compare Options

- `--output` or `-o`: Output format (terminal, json)

## Examples

### Basic Analysis

```bash
# Analyze current directory
uv run code_analyzer analyze .

# Analyze with complexity metrics
uv run code_analyzer analyze . --complexity

# Analyze and export to JSON
uv run code_analyzer analyze . --export json --export-dir ./reports
```

### Advanced Usage

```bash
# Export to multiple formats
uv run code_analyzer analyze . --export json,html,css --export-dir ./reports

# Limit top files display
uv run code_analyzer analyze . --top-files 50

# Compare two analyses
uv run code_analyzer compare reports/2025-01-01.json reports/2025-01-15.json
```

## Configuration

Create a `.refactoroscope.yml` file in your project root for custom settings:

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