---
layout: default
title: Refactoroscope
---

# Refactoroscope Documentation

Welcome to the Refactoroscope documentation!

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
uv run refactoroscope analyze .
uv run refactoroscope analyze . --complexity
uv run refactoroscope analyze . --export json,html --export-dir ./reports
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
- [Use Cases](use-cases.md)
- [Contributing](contributing.md)
- [Real-time Watching](watch.md)
- [AI-Powered Analysis](ai.md)
- [Duplicate Code Detection](duplicates.md)
- [Unused Code Detection](unused_code.md)
- [Unused File Detection](unused_file_detection.md)
- [Advanced Refactoring Tools](advanced_refactoring_tools.md)
- [Release Notes v0.4.1](release-notes-v0.4.1.md)
- [Release Notes v0.2.0](release-notes-v0.2.0.md)