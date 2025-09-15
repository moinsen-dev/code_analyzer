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
- `duplicates`: Analyze for duplicate code
- `unused`: Analyze for unused code
- `unused-files`: Analyze for unused files
- `refactor-plan`: Generate an AI-based refactoring plan

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

### AI (--ai/--no-ai)
Enable/disable AI-powered code suggestions during analysis.

Default: `no-ai`

Example:
```bash
uv run refactoroscope analyze . --ai
```

When enabled, this option will:
1. Enable AI-powered code quality suggestions
2. Analyze complex files with configured AI providers
3. Display AI-generated suggestions in the "Code Smells Detected" section
4. Provide intelligent insights on code readability, performance, potential bugs, and security issues

### Duplicates Options

- `--type`: Type of duplicates to detect (exact, renamed, modified, semantic)
- `--min-similarity`: Minimum similarity threshold (0.0 to 1.0)

### Unused Code Options

- `--confidence`: Confidence threshold for reporting (0.0 to 1.0)

### Unused Files Options

- `--confidence`: Confidence threshold for reporting (0.0 to 1.0)
- `--entry-point`: Specify entry point files

## Tech Stack Analysis and Tool Execution

### Check (--check)
Enable tech stack detection and run appropriate tools for each detected tech stack in subfolders.

Default: Disabled

Example:
```bash
uv run refactoroscope analyze . --check
```

This option will:
1. Detect technology stacks in all subfolders
2. Run appropriate linters, formatters, and type checkers for each detected tech stack
3. Check for outdated packages
4. Display results in terminal

## AI-Powered Refactoring Plan Generation

### Provider (-p, --provider)
AI provider to use for refactoring plan generation.

Choices: `openai`, `anthropic`, `google`, `ollama`, `qwen`
Default: `openai`

### Output (-o, --output)
Output file for the refactoring plan.

Default: `refactor_plan.md`

Example:
```bash
uv run refactoroscope refactor-plan . --provider openai --output my_plan.md
```

## Examples

### Basic Analysis

```bash
# Analyze current directory
uv run refactoroscope analyze .

# Analyze specific directory
uv run refactoroscope analyze /path/to/project

# Disable complexity analysis (if needed)
uv run refactoroscope analyze . --no-complexity

# Enable AI-powered suggestions
uv run refactoroscope analyze . --ai
```

### Real-time Watching

```bash
# Watch current directory for changes
uv run refactoroscope watch .

# Watch specific directory
uv run refactoroscope watch /path/to/project

# Enable AI-powered suggestions during watching
uv run refactoroscope watch . --ai
```

### Duplicate Code Detection

```bash
# Analyze for duplicate code
uv run refactoroscope duplicates src/

# Analyze for exact duplicates only
uv run refactoroscope duplicates src/ --type exact

# Find similar code with minimum similarity threshold
uv run refactoroscope duplicates src/ --min-similarity 0.8

# Focus on renamed clones
uv run refactoroscope duplicates src/ --type renamed
```

### Unused Code Detection

```bash
# Analyze for unused code
uv run refactoroscope unused src/

# Get JSON output for unused code
uv run refactoroscope unused src/ --output json
```

### Unused File Detection

```bash
# Analyze for unused files
uv run refactoroscope unused-files src/

# Analyze for unused files with confidence threshold
uv run refactoroscope unused-files src/ --confidence 0.7

# Get JSON output for unused files
uv run refactoroscope unused-files src/ --output json
```

### Tech Stack Analysis and Tool Execution

```bash
# Analyze current directory and run appropriate tools for detected tech stacks
uv run refactoroscope analyze . --check

# This will:
# 1. Detect technology stacks in all subfolders
# 2. Run appropriate linters, formatters, and type checkers for each stack
# 3. Check for outdated packages
# 4. Display results in terminal
```

### AI-Powered Refactoring Plan Generation

```bash
# Generate an AI-based refactoring plan for your project
uv run refactoroscope refactor-plan .

# Generate refactoring plan with specific AI provider
uv run refactoroscope refactor-plan . --provider openai

# Save refactoring plan to specific file
uv run refactoroscope refactor-plan . --output my_plan.md
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