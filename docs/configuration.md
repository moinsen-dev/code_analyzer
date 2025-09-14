---
layout: default
title: Configuration
---

The Refactoroscope can be configured using a `.refactoroscope.yml` file in your project root.

This file allows you to customize language-specific settings, analysis rules, and output preferences.

## Creating a Configuration File

To create a configuration file, run:

```bash
refactoroscope init
```

This will create a `.refactoroscope.yml` file with default settings.

To overwrite an existing configuration file:

```bash
uv run code_analyzer init --force
```

## Configuration File Structure

```yaml
version: 1.0

languages:
  # Language-specific settings
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15

analysis:
  # File patterns to ignore
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"
  
  # Complexity analysis options
  complexity:
    include_docstrings: false
    count_assertions: true
  
  # Analysis thresholds
  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

output:
  # Output format
  format: "terminal"  # terminal, json, html, csv
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
```

## Language-Specific Settings

Configure settings for specific programming languages:

```yaml
languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  javascript:
    max_line_length: 100
    complexity_threshold: 15
  typescript:
    max_line_length: 100
    complexity_threshold: 15
  java:
    max_line_length: 100
    complexity_threshold: 12
```

## Analysis Configuration

### Ignore Patterns

Specify file patterns to ignore during analysis:

```yaml
analysis:
  ignore_patterns:
    # Generated files
    - "*.generated.*"
    - "*_pb2.py"
    # Build artifacts
    - "dist/"
    - "build/"
    - "*.min.js"
    # Dependencies
    - "node_modules/"
    - "vendor/"
    # Version control
    - ".git/"
    # IDE files
    - ".vscode/"
    - ".idea/"
```

### Complexity Options

Configure complexity analysis behavior:

```yaml
analysis:
  complexity:
    # Include docstrings in complexity calculations
    include_docstrings: false
    # Count assertions in complexity calculations
    count_assertions: true
```

### Thresholds

Set thresholds for code quality analysis:

```yaml
analysis:
  thresholds:
    # Maximum lines in a file before it's considered too long
    file_too_long: 500
    # Maximum complexity for a function before it's considered too complex
    function_too_complex: 20
    # Maximum members in a class before it's considered too large
    class_too_large: 1000
```

## Output Configuration

Configure output preferences:

```yaml
output:
  # Output format (terminal, json, html, csv)
  format: "terminal"
  # Theme for terminal output
  theme: "monokai"
  # Show recommendations in output
  show_recommendations: true
  # Default export directory
  export_path: "./reports"
```

## Environment Variables

The following environment variables can be used to configure the analyzer:

- `CODEANALYZER_CONFIG_PATH`: Path to configuration file
- `CODEANALYZER_EXPORT_PATH`: Default export directory
- `CODEANALYZER_THEME`: Default terminal theme

## Example Configurations

### Web Development Project

```yaml
version: 1.0

languages:
  javascript:
    max_line_length: 100
    complexity_threshold: 15
  typescript:
    max_line_length: 100
    complexity_threshold: 15

analysis:
  ignore_patterns:
    - "node_modules/"
    - "dist/"
    - "build/"
    - "*.min.js"
    - "*.map"
  
  thresholds:
    file_too_long: 300
    function_too_complex: 15
    class_too_large: 500

output:
  format: "terminal"
  theme: "dracula"
  show_recommendations: true
  export_path: "./analysis"
```

### Python Project

```yaml
version: 1.0

languages:
  python:
    max_line_length: 88
    complexity_threshold: 10

analysis:
  ignore_patterns:
    - "__pycache__/"
    - "*.pyc"
    - "*.pyo"
    - ".pytest_cache/"
    - ".coverage"
  
  complexity:
    include_docstrings: false
    count_assertions: true
  
  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

output:
  format: "terminal"
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
```

### Multi-Language Project

```yaml
version: 1.0

languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  javascript:
    max_line_length: 100
    complexity_threshold: 15
  typescript:
    max_line_length: 100
    complexity_threshold: 15
  java:
    max_line_length: 100
    complexity_threshold: 12

analysis:
  ignore_patterns:
    - "node_modules/"
    - "dist/"
    - "build/"
    - "__pycache__/"
    - "*.jar"
    - "*.class"
  
  thresholds:
    file_too_long: 400
    function_too_complex: 18
    class_too_large: 750

output:
  format: "terminal"
  theme: "github"
  show_recommendations: true
  export_path: "./analysis_reports"
```