---
layout: default
title: Usage Guide
---

# Usage Guide

## Basic Analysis

### Analyzing a Directory

To analyze the current directory:

```bash
uv run refactoroscope analyze .
```

To analyze a specific directory:

```bash
uv run refactoroscope analyze /path/to/project
```

### Including Complexity Analysis

To include detailed complexity metrics:

```bash
uv run refactoroscope analyze . --complexity
```

## Output Formats

### Terminal Output (Default)

```bash
uv run refactoroscope analyze . --output terminal
```

### Exporting Results

Export to JSON:

```bash
uv run refactoroscope analyze . --export json --export-dir ./reports
```

Export to multiple formats:

```bash
uv run refactoroscope analyze . --export json,html --export-dir ./reports
```

## Command Line Options

### Main Commands

- `analyze`: Analyze a codebase
- `compare`: Compare two analysis reports
- `init`: Initialize a configuration file
- `watch`: Watch a codebase for changes
- `ai`: Analyze codebase with AI-powered suggestions
- `duplicates`: Analyze for duplicate code
- `unused`: Analyze for unused code
- `unused-files`: Analyze for unused files

### Analyze Options

- `--complexity` or `-c`: Include complexity analysis
- `--output` or `-o`: Output format (terminal, json, html, csv)
- `--export` or `-e`: Export formats (json, html, csv)
- `--export-dir`: Directory for exports
- `--top-files` or `-t`: Number of top files to display

### Compare Options

- `--output` or `-o`: Output format (terminal, json)

### Watch Options

- `--ai`: Enable AI-powered suggestions during watching
- `--no-complexity` or `-C`: Disable complexity analysis

### AI Options

- `--provider`: Specify which AI provider to use (openai, anthropic, google, ollama, qwen)
- `--no-cache`: Disable caching of AI results

### Duplicates Options

- `--type`: Type of duplicates to detect (exact, renamed, modified, semantic)
- `--min-similarity`: Minimum similarity threshold (0.0 to 1.0)

### Unused Code Options

- `--confidence`: Confidence threshold for reporting (0.0 to 1.0)

### Unused Files Options

- `--confidence`: Confidence threshold for reporting (0.0 to 1.0)
- `--entry-point`: Specify entry point files

## Examples

### Basic Analysis

```bash
# Analyze current directory
uv run refactoroscope analyze .

# Analyze with complexity metrics
uv run refactoroscope analyze . --complexity

# Analyze and export to JSON
uv run refactoroscope analyze . --export json --export-dir ./reports
```

### Real-time Watching

```bash
# Watch current directory
uv run refactoroscope watch .

# Watch with AI suggestions
uv run refactoroscope watch . --ai

# Watch without complexity analysis
uv run refactoroscope watch . --no-complexity
```

### AI-Powered Analysis

```bash
# Analyze with AI
uv run refactoroscope ai .

# Analyze with specific provider
uv run refactoroscope ai . --provider openai

# Analyze with AI during regular analysis
uv run refactoroscope analyze . --ai
```

### Duplicate Code Detection

```bash
# Analyze for duplicates
uv run refactoroscope duplicates .

# Analyze for exact duplicates only
uv run refactoroscope duplicates . --type exact

# Analyze with custom similarity threshold
uv run refactoroscope duplicates . --min-similarity 0.9
```

### Unused Code Detection

```bash
# Analyze for unused code
uv run refactoroscope unused .

# Analyze with custom confidence threshold
uv run refactoroscope unused . --confidence 0.8
```

### Unused File Detection

```bash
# Analyze for unused files
uv run refactoroscope unused-files .

# Analyze with custom confidence threshold
uv run refactoroscope unused-files . --confidence 0.8

# Specify entry points
uv run refactoroscope unused-files . --entry-point main.py --entry-point app.py
```

### Advanced Usage

```bash
# Export to multiple formats
uv run refactoroscope analyze . --export json,html,css --export-dir ./reports

# Limit top files display
uv run refactoroscope analyze . --top-files 50

# Compare two analyses
uv run refactoroscope compare reports/2025-01-01.json reports/2025-01-15.json
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