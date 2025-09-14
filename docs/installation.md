---
layout: default
title: Installation Guide
---

# Installation

Code Analyzer can be installed in several ways:

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Installing uv

If you don't have uv installed, you can install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installing Refactoroscope

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourorg/code-insight-analyzer.git
   cd code-insight-analyzer
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Using pip (when available)

```bash
pip install code_analyzer
```

## Verifying Installation

To verify that the installation was successful, run:

```bash
uv run code_analyzer --help
```

You should see the help output showing available commands.

## System Requirements

- **Operating Systems**: Windows, macOS, Linux
- **Memory**: Minimum 512MB RAM (recommended 1GB+ for large projects)
- **Disk Space**: Varies based on project size
- **Python**: 3.13 or higher

## Docker Support (Planned)

A Docker image will be available for easier deployment:

```dockerfile
FROM python:3.13-slim

# Install uv
RUN pip install uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

ENTRYPOINT ["uv", "run", "code_analyzer"]
```