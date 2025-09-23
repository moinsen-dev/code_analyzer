# Refactoroscope

[![Build Status](https://github.com/moinsen-dev/refactoroscope/actions/workflows/ci.yml/badge.svg)](https://github.com/moinsen-dev/refactoroscope/actions)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/moinsen-dev/refactoroscope)](LICENSE)
[![Code Coverage](https://img.shields.io/codecov/c/github/moinsen-dev/refactoroscope)](https://codecov.io/gh/moinsen-dev/refactoroscope)
[![PyPI version](https://badge.fury.io/py/refactoroscope.svg)](https://badge.fury.io/py/refactoroscope)
[![CI/CD Integration](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20%26%20GitLab%20CI-blue)](docs/ci-cd-integration.md)

![Refactoroscope Icon](code-analyzer-icon.png)

A Python-based command-line tool that provides comprehensive analysis of source code repositories. Think of it as an **MRI scanner for your codebase** - it doesn't just show you what's there, but reveals the health and complexity of your code structure.

![Refactoroscope Wallpaper](code-analyzer-wallpaper.png)

## Features

- Scans directories recursively for source code files
- Respects `.gitignore` patterns at all directory levels
- Counts lines of code per file
- Displays file sizes in human-readable format
- Sorts results by line count
- Beautiful terminal output using Rich
- Code complexity analysis (Cyclomatic, Cognitive, Halstead)
- Duplicate code detection using AST-based analysis
- **Unused code detection using AST-based analysis**
- **Unused file detection using dependency graph analysis**
- **AI-powered code quality suggestions**
- **Advanced refactoring tools with AI-powered refactoring plan generation**
- **Tech stack detection for 10+ programming languages (Python, JavaScript/TypeScript, Flutter, Go, Rust, Ruby, PHP, Java, Kotlin)**
- **Integrated tool execution for each detected tech stack**
- **Outdated package detection for all supported tech stacks**
- Export results to JSON/CSV/HTML
- Configuration file support (.refactoroscope.yml)
- Multi-language support (60+ programming languages)
- Performance optimizations with parallel processing
- CI/CD integration support (GitHub Actions, GitLab CI)
- Real-time file watching for live code analysis
- Advanced AST-based duplicate code detection with clone type classification

## Duplicate Code Detection

The Refactoroscope provides advanced AST-based duplicate code detection with the following features:

- **Clone Type Classification**: Identifies different types of code clones:
  - **Exact Clones** (Type-1): Identical code except for comments and whitespace
  - **Renamed Clones** (Type-2): Syntactically identical with identifier renames
  - **Modified Clones** (Type-3): Semantically similar with small modifications
  - **Semantic Clones** (Type-4): Functionally equivalent but syntactically different

- **Cross-File Detection**: Finds duplicate code patterns across different files in your project

- **Similarity Scoring**: Provides quantitative similarity measures between code blocks (0.0 to 1.0)

- **Performance Optimizations**: Uses caching and global indexing for efficient analysis of large codebases

The duplicate detection can be customized with the `duplicates` command:

```bash
# Analyze for exact duplicates only (complexity analysis is now included by default)
uv run refactoroscope duplicates src/ --type exact

# Find similar code with minimum similarity threshold
uv run refactoroscope duplicates src/ --min-similarity 0.8

# Focus on renamed clones
uv run refactoroscope duplicates src/ --type renamed
```

### Installation

Refactoroscope can be installed in several ways depending on your needs. **Note: AI providers (OpenAI, Anthropic, Google) are now required dependencies.**

#### Method 1: Install from PyPI (Recommended for most users)

```bash
pip install refactoroscope
```

This installs Refactoroscope globally on your system and makes it available as a command-line tool. **AI providers are now included by default.**

#### Method 2: Install with uv (Recommended for developers)

First, install [uv](https://github.com/astral-sh/uv) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install Refactoroscope globally:

```bash
uv tool install refactoroscope
```

#### Method 3: Install from source (Recommended for contributors)

1. Clone the repository:
   ```bash
   git clone https://github.com/moinsen-dev/refactoroscope.git
   cd refactoroscope
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Basic Analysis

```bash
# Analyze current directory (complexity analysis is now enabled by default)
uv run refactoroscope analyze .

# Analyze specific directory
uv run refactoroscope analyze /path/to/project

# Disable complexity analysis (if needed)
uv run refactoroscope analyze . --no-complexity

# Enable AI-powered suggestions
uv run refactoroscope analyze . --ai
```

### AI-Powered Analysis

Refactoroscope provides AI-powered code quality suggestions integrated directly into the main analysis command. The AI analysis provides intelligent insights on code readability, performance, potential bugs, and security issues.

```bash
# Analyze with AI-powered suggestions
uv run refactoroscope analyze . --ai

# Enable AI suggestions during watching
uv run refactoroscope watch . --ai

# Check tech stacks and run appropriate tools for each subfolder
uv run refactoroscope analyze . --check

# Generate an AI-based refactoring plan for the codebase
uv run refactoroscope refactor-plan .
```

#### AI Provider Configuration

To use AI-powered features, you need to configure at least one AI provider in your `.refactoroscope.yml` configuration file:

```yaml
# AI configuration
ai:
  # Enable AI-powered code suggestions
  enable_ai_suggestions: true
  
  # Maximum file size to analyze with AI (in bytes)
  max_file_size: 50000
  
  # Whether to cache AI analysis results
  cache_results: true
  
  # Cache time-to-live in seconds
  cache_ttl: 3600
  
  # Preference order for AI providers
  provider_preferences:
    - "openai"
    - "anthropic"
    - "google"
    - "ollama"
    - "qwen"
  
  # Provider configurations
  providers:
    openai:
      # API key (can also be set via OPENAI_API_KEY environment variable)
      # api_key: "your-openai-api-key"
      
      # Model to use
      model: "gpt-3.5-turbo"
      
      # Whether this provider is enabled
      enabled: true
    
    anthropic:
      # API key (can also be set via ANTHROPIC_API_KEY environment variable)
      # api_key: "your-anthropic-api-key"
      
      # Model to use
      model: "claude-3-haiku-20240307"
      
      # Whether this provider is enabled
      enabled: true
    
    google:
      # API key (can also be set via GOOGLE_API_KEY environment variable)
      # api_key: "your-google-api-key"
      
      # Model to use
      model: "gemini-pro"
      
      # Whether this provider is enabled
      enabled: true
    
    ollama:
      # Ollama doesn't require API keys
      
      # Model to use
      model: "llama2"
      
      # Base URL for Ollama (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true
    
    qwen:
      # Qwen doesn't require API keys for local installations
      
      # Model to use
      model: "qwen"
      
      # Base URL for Qwen (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true
```

### Tech Stack Analysis and Tool Execution

Refactoroscope can automatically detect technology stacks in your project and run the appropriate tools for each stack:

```bash
# Analyze current directory and run appropriate tools for detected tech stacks
uv run refactoroscope analyze . --check

# This will:
# 1. Detect technology stacks (Python, JavaScript, Flutter, Go, Rust, etc.)
# 2. Run appropriate linters, formatters, and type checkers for each stack
# 3. Check for outdated packages
# 4. Display results in terminal

# Example output for a Python project:
# Folder: src/
# Detected Tech Stacks: python
# Tool Results:
#   • lint_ruff: ✓ Passed
#   • format_black: ✗ Failed (would reformat src/main.py)
#   • type_mypy: ✓ Passed
# Outdated Packages:
#   • requests: 2.31.0 -> 2.32.3
```

### AI-Powered Refactoring Plan Generation

Generate comprehensive, AI-based refactoring plans for your codebase:

```bash
# Generate an AI-based refactoring plan for your project
uv run refactoroscope refactor-plan .

# Generate refactoring plan with specific AI provider
uv run refactoroscope refactor-plan . --provider openai

# Save refactoring plan to specific file
uv run refactoroscope refactor-plan . --output my_refactoring_plan.md

# This will:
# 1. Analyze your codebase
# 2. Detect complexity hotspots, duplicate code, code smells
# 3. Generate a phased refactoring plan with implementation timeline
# 4. Provide risk assessment and success metrics
```

#### Supported AI Providers

1. **OpenAI**: Supports GPT models (GPT-3.5, GPT-4, etc.)
2. **Anthropic**: Supports Claude models
3. **Google**: Supports Gemini models
4. **Ollama**: Supports locally-run models (no API key required)

For cloud-based providers, you can set API keys via environment variables:
- `OPENAI_API_KEY` for OpenAI
- `ANTHROPIC_API_KEY` for Anthropic
- `GOOGLE_API_KEY` for Google

### Real-time Watching

```bash
# Watch current directory for changes (complexity analysis is now enabled by default)
uv run refactoroscope watch .

# Enable AI-powered suggestions during watching
uv run refactoroscope watch . --ai

# Disable complexity analysis (if needed)
uv run refactoroscope watch . --no-complexity
```

### Output Formats

```bash
# Display in terminal (default)
uv run refactoroscope analyze . --output terminal

# Export to JSON
uv run refactoroscope analyze . --export json --export-dir ./reports

# Export to multiple formats
uv run refactoroscope analyze . --export json,html --export-dir ./reports
```

### Advanced Usage

```bash
# Compare two analysis reports
uv run refactoroscope compare reports/report1.json reports/report2.json

# Initialize configuration file
uv run refactoroscope init

# Analyze for duplicate code with advanced options
uv run refactoroscope duplicates src/ --type exact --min-similarity 0.9

# Analyze for unused code
uv run refactoroscope unused src/

# Analyze for unused files
uv run refactoroscope unused-files src/

# Analyze for unused files with confidence threshold
uv run refactoroscope unused-files src/ --confidence 0.7
```

### Unused Code Detection

Refactoroscope can identify potentially unused code in your Python projects using AST-based static analysis. This feature helps you identify dead code that can be safely removed to reduce technical debt.

The unused code detection identifies:
- Unused functions and methods
- Unused classes
- Unused variables
- Unused imports

```bash
# Analyze for unused code
uv run refactoroscope unused src/

# Get JSON output for unused code
uv run refactoroscope unused src/ --output json
```

The analysis provides confidence scores for each finding to help you distinguish between likely unused code and potential false positives.

### Unused File Detection

Refactoroscope can also identify completely unused files in your Python projects using dependency graph analysis. This feature helps you identify entire files that are never imported by any other file in your project.

```bash
# Analyze for unused files
uv run refactoroscope unused-files src/

# Analyze for unused files with confidence threshold
uv run refactoroscope unused-files src/ --confidence 0.7

# Get JSON output for unused files
uv run refactoroscope unused-files src/ --output json
```

The unused file detection uses the following approach:
1. Builds a dependency graph of all Python files in your project
2. Identifies entry points (files with `__main__` guards, common entry point names)
3. Performs reachability analysis to find files that are not reachable from entry points
4. Provides confidence scores to help distinguish between truly unused files and potential false positives

## Supported Languages

The Refactoroscope supports 60+ programming languages:

- **Primary**: Python, JavaScript/TypeScript, Java, C#, C++/C, Go, Rust
- **Mobile**: Dart/Flutter, Swift, Kotlin
- **Web**: HTML, CSS/SCSS, Vue, React, Svelte
- **Scripting**: PHP, Ruby
- **Configuration**: YAML, JSON, TOML, XML
- **Data**: SQL, GraphQL
- **Documentation**: Markdown, reStructuredText

## Configuration

Create a `.refactoroscope.yml` file in your project root:

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

# AI configuration
ai:
  # Enable AI-powered code suggestions
  enable_ai_suggestions: false
  
  # Maximum file size to analyze with AI (in bytes)
  max_file_size: 50000
  
  # Whether to cache AI analysis results
  cache_results: true
  
  # Cache time-to-live in seconds
  cache_ttl: 3600
  
  # Preference order for AI providers
  provider_preferences:
    - "openai"
    - "anthropic"
    - "google"
    - "ollama"
  
  # Provider configurations
  providers:
    openai:
      # API key (can also be set via OPENAI_API_KEY environment variable)
      # api_key: "your-openai-api-key"
      
      # Model to use
      model: "gpt-3.5-turbo"
      
      # Whether this provider is enabled
      enabled: false
    
    anthropic:
      # API key (can also be set via ANTHROPIC_API_KEY environment variable)
      # api_key: "your-anthropic-api-key"
      
      # Model to use
      model: "claude-3-haiku-20240307"
      
      # Whether this provider is enabled
      enabled: false
    
    google:
      # API key (can also be set via GOOGLE_API_KEY environment variable)
      # api_key: "your-google-api-key"
      
      # Model to use
      model: "gemini-pro"
      
      # Whether this provider is enabled
      enabled: false
    
    ollama:
      # Ollama doesn't require API keys
      
      # Model to use
      model: "llama2"
      
      # Base URL for Ollama (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: false
```

## CI/CD Integration

Refactoroscope provides built-in support for popular CI/CD platforms:

### GitHub Actions

To integrate Refactoroscope into your GitHub Actions workflow, create a workflow file in `.github/workflows/`:

```yaml
name: Code Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Code Analysis
        uses: moinsen-dev/refactoroscope@v0.2.0
        with:
          args: analyze . --complexity --export json,html
```

Alternatively, you can install and run it directly:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3

- name: Install Refactoroscope
  run: |
    uv pip install refactoroscope

- name: Run analysis
  run: |
    refactoroscope analyze . --complexity --export json,html --export-dir ./reports
```

### GitLab CI

For GitLab CI, add this to your `.gitlab-ci.yml`:

```yaml
analyze:
  stage: test
  script:
    - pip install refactoroscope
    - refactoroscope analyze . --complexity --export json,html --export-dir ./reports
  artifacts:
    paths:
      - reports/
```

See [CI/CD Integration Guide](docs/ci-cd-integration.md) for more detailed instructions.

## Documentation

For detailed documentation, visit our [GitHub Pages site](https://moinsen-dev.github.io/refactoroscope/).

- [Real-time Watching](docs/watch.md)
- [AI-Powered Analysis](docs/ai.md)
- [Duplicate Code Detection](docs/duplicates.md)
- [Unused Code Detection](docs/unused_code.md)
- [Unused File Detection](docs/unused_file_detection.md)

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for more information.

## Release Process

New versions are automatically published to PyPI when a new tag is created following the pattern `v*.*.*`. To release a new version:

1. Update the version in `pyproject.toml` and `setup.py`
2. Create a new tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
3. Push the tag: `git push origin v1.0.0`
4. The GitHub Actions workflow will automatically build and publish to PyPI