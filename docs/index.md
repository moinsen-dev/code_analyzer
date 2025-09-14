---
layout: default
title: Refactoroscope
---

# Code Analyzer Documentation

Welcome to the Code Analyzer documentation!

A Python-based command-line tool that provides comprehensive analysis of source code repositories. Think of it as an **MRI scanner for your codebase** - it doesn't just show you what's there, but reveals the health and complexity of your code structure.

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
- Configuration file support (.refactoroscope.yml)
- Multi-language support (60+ programming languages)
- Performance optimizations with parallel processing
- CI/CD integration support (GitHub Actions, GitLab CI)

## Installation

First, install [uv](https://github.com/astral-sh/uv) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the dependencies:

```bash
uv sync
```

## Quick Start

```bash
uv run code_analyzer analyze .
uv run code_analyzer analyze . --complexity
uv run code_analyzer analyze . --export json,html --export-dir ./reports
```

## Supported Languages

The Refactoroscope supports 60+ programming languages:

- **Primary**: Python, JavaScript/TypeScript, Java, C#, C++/C, Go, Rust
- **Mobile**: Dart/Flutter, Swift, Kotlin
- **Web**: HTML, CSS/SCSS, Vue, React, Svelte
- **Scripting**: PHP, Ruby
- **Configuration**: YAML, JSON, TOML, XML
- **Data**: SQL, GraphQL
- **Documentation**: Markdown, reStructuredText

## Documentation

- [Installation Guide](installation.md)
- [Usage Guide](usage.md)
- [Configuration](configuration.md)
- [API Reference](api.md)
- [Examples](examples.md)
- [Contributing](contributing.md)