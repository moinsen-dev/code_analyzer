# Refactoroscope - Project Context

## IMPORTANT:
- Before committing, ensure all tests pass and code is formatted with `black` and alway ask the user for confirmation before committing.

## Project Overview

The **Refactoroscope** is a Python-based command-line tool designed to provide comprehensive analysis of source code repositories. It functions as an "MRI scanner for your codebase," revealing not just what's there but also the health and complexity of your code structure.

### Key Features
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

## Technology Stack

- **Runtime**: Python 3.13
- **Package Manager**: uv
- **Core Dependencies**: rich, radon, pygments, pydantic, typer
- **Analysis Tools**: ast (builtin), lizard, flake8
- **Export Tools**: pandas, jinja2, openpyxl
- **Development Tools**: pytest, ruff, black, mypy

## Project Status

The project is now in active development with most core features implemented:

- Basic file scanning and line counting ✅
- GitIgnore support ✅
- Rich terminal output ✅
- Python 3.13 compatibility ✅
- uv package manager integration ✅
- Code complexity analysis ✅
- Export to JSON/CSV/HTML ✅
- Configuration file support ✅
- Code smell detection ✅
- Historical tracking (compare analyses) ✅
- Duplicate code detection ✅
- Multi-language complexity metrics ✅
- Performance optimizations ✅

## Development Workflow

### Branch Strategy
- `develop` branch for ongoing development
- Feature branches should be created from `develop`

### Commands

1. **Setup**:
   ```bash
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Clone repository
   git clone <repository-url>
   cd refactoroscope

   # Install dependencies
   uv sync
   ```

2. **Running the Tool**:
   ```bash
   # Basic usage with uv (complexity analysis is now enabled by default)
   uv run refactoroscope analyze .

   # Disable complexity analysis (if needed)
   uv run refactoroscope analyze . --no-complexity

   # Export to multiple formats
   uv run refactoroscope analyze . \\
     --output terminal \\
     --export json,html \\
     --export-dir ./reports
   ```

## Development Guidelines

### Code Structure
The implemented architecture includes:
- CLI Entry Point
- Configuration Manager
- Scanner Engine
- GitIgnore Parser
- File Detector
- Analyzers (Line Counter, Size Calculator, Complexity Analyzer)
- Code Smell Detector
- Duplicate Code Detector
- Results Aggregator
- Output Formatters (Terminal Display, JSON Export, HTML Report, CSV Export)

### Domain Models
Implemented data models:
- FileMetrics
- HalsteadMetrics
- ComplexityMetrics
- Duplication
- CodeInsights
- AnalysisReport

### Testing Strategy
- Unit Tests: > 90% coverage target ✅ (Current: ~85%)
- Integration Tests: All major workflows ✅
- Performance Tests: Benchmark suite 🟡 (Basic benchmarks implemented)
- Regression Tests: Historical compatibility ✅

## Environment Configuration

The project uses a local AI setup with Ollama:
- OPENAI_BASE_URL: "http://localhost:11434/v1"
- OPENAI_API_KEY: "ollama" (any string works locally)
- OPENAI_MODEL: "qwen3:30b"

## Next Steps

Based on the PRD, the next steps are:
1. Implement CI/CD integrations
2. Create web dashboard
3. Develop IDE plugins
4. Add real-time file watching
5. Implement AI-powered code quality suggestions
6. Polish documentation and create tutorial videos
7. Prepare for v1.0 release