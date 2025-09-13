# Code Insight Analyzer - Project Context

## Project Overview

The **Code Insight Analyzer** is a Python-based command-line tool designed to provide comprehensive analysis of source code repositories. It functions as an "MRI scanner for your codebase," revealing not just what's there but also the health and complexity of your code structure.

### Key Features
- Scans directories recursively for source code files
- Respects `.gitignore` patterns at all directory levels
- Counts lines of code per file
- Displays file sizes in human-readable format
- Sorts results by line count
- Beautiful terminal output using Rich
- Code complexity analysis (Cyclomatic, Cognitive)
- Export results to JSON/CSV/HTML
- Configuration file support (.codeinsight.yml)

## Technology Stack

- **Runtime**: Python 3.13
- **Package Manager**: uv
- **Core Dependencies**: rich, radon, pygments, pydantic, typer
- **Analysis Tools**: ast (builtin), lizard, flake8
- **Export Tools**: pandas, jinja2, openpyxl
- **Development Tools**: pytest, ruff, black, mypy

## Project Status

This is a new project in the early development phase:
- No commits have been made yet to the git repository
- The repository is currently on the `develop` branch
- Only documentation files exist (PRD.md, QWEN.md) and a .env.bak file
- The project structure is not yet established

## Development Workflow

### Branch Strategy
- `develop` branch for ongoing development
- Feature branches should be created from `develop`

### Commands
Since the project structure is not yet established, these are the planned commands based on the PRD:

1. **Setup**:
   ```bash
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Clone repository (when available)
   git clone <repository-url>
   cd code-insight-analyzer
   
   # Install dependencies (when pyproject.toml is available)
   uv sync
   ```

2. **Running the Tool**:
   ```bash
   # Basic usage with uv
   uv run codeinsight analyze .
   
   # With complexity analysis
   uv run codeinsight analyze . --complexity
   
   # Export to multiple formats
   uv run codeinsight analyze . \
     --output terminal \
     --export json,html \
     --export-dir ./reports
   ```

## Development Guidelines

### Code Structure
Based on the PRD, the planned architecture includes:
- CLI Entry Point
- Configuration Manager
- Scanner Engine
- GitIgnore Parser
- File Detector
- Analyzers (Line Counter, Size Calculator, Complexity Analyzer)
- Results Aggregator
- Output Formatters (Terminal Display, JSON Export, HTML Report, CSV Export)

### Domain Models
Key data models planned for implementation:
- FileMetrics
- ComplexityMetrics
- CodeInsights
- AnalysisReport

### Testing Strategy
- Unit Tests: > 90% coverage target
- Integration Tests: All major workflows
- Performance Tests: Benchmark suite
- Regression Tests: Historical compatibility

## Environment Configuration

The project uses a local AI setup with Ollama:
- OPENAI_BASE_URL: "http://localhost:11434/v1"
- OPENAI_API_KEY: "ollama" (any string works locally)
- OPENAI_MODEL: "qwen3:30b"

## Next Steps

Based on the PRD, the immediate next steps are:
1. Set up the basic project structure
2. Implement Python 3.13 compatibility
3. Integrate uv package manager
4. Create core CLI framework with Typer
5. Implement basic file scanning and line counting (already marked as complete in PRD)
6. Add GitIgnore support
7. Implement Rich terminal output
8. Add complexity analysis features

## File Structure (Planned)

```
code-insight-analyzer/
├── src/
│   └── codeinsight/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── config.py           # Configuration manager
│       ├── scanner.py          # Scanner engine
│       ├── gitignore.py        # GitIgnore parser
│       ├── detector.py         # File detector
│       ├── analyzers/          # Analysis modules
│       │   ├── __init__.py
│       │   ├── line_counter.py
│       │   ├── size_calculator.py
│       │   └── complexity.py
│       ├── models/             # Domain models
│       │   ├── __init__.py
│       │   └── metrics.py
│       └── exporters/          # Export functionality
│           ├── __init__.py
│           ├── json.py
│           ├── csv.py
│           └── html.py
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_scanner.py
│   ├── test_analyzers/
│   └── test_exporters/
├── docs/
├── examples/
├── reports/                    # Default export directory
├── pyproject.toml              # Project configuration
├── uv.lock                     # Dependency lock file
├── .codeinsight.yml           # Default configuration file
├── .gitignore
└── README.md
```