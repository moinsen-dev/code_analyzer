---
layout: default
title: API Reference
---

# API Reference

## CLI Commands

### analyze

Analyzes a codebase and displays results.

```bash
refactoroscope analyze [PATH] [OPTIONS]
```

**Arguments:**
- `PATH`: Path to analyze (default: current directory)

**Options:**
- `--complexity` or `-c`: Include complexity analysis
- `--output` or `-o`: Output format (terminal, json, html, csv) [default: terminal]
- `--export` or `-e`: Export formats (json, html, csv)
- `--export-dir`: Directory for exports [default: ./reports]
- `--top-files` or `-t`: Number of top files to display [default: 20]
- `--help`: Show help message

### compare

Compares two analysis reports.

```bash
refactoroscope compare [REPORT1_PATH] [REPORT2_PATH] [OPTIONS]
```

**Arguments:**
- `REPORT1_PATH`: First report file (JSON)
- `REPORT2_PATH`: Second report file (JSON)

**Options:**
- `--output` or `-o`: Output format (terminal, json) [default: terminal]
- `--help`: Show help message

### init

Initializes a .refactoroscope.yml configuration file.

```bash
refactoroscope init [PATH] [OPTIONS]
```

**Arguments:**
- `PATH`: Path to initialize configuration [default: current directory]

**Options:**
- `--force` or `-f`: Overwrite existing configuration file
- `--help`: Show help message

## Configuration File

The `.refactoroscope.yml` file supports the following configuration options:

### version

Configuration file version.

```yaml
version: 1.0
```

### languages

Language-specific settings.

```yaml
languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15
```

### analysis

Analysis rules and thresholds.

```yaml
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
```

### output

Output preferences.

```yaml
output:
  format: "terminal"  # terminal, json, html, csv
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
```

## Data Models

### FileMetrics

Metrics for a single file.

```python
@dataclass
class FileMetrics:
    path: Path
    relative_path: str
    language: Language
    lines_of_code: int
    blank_lines: int
    comment_lines: int
    size_bytes: int
    last_modified: datetime
```

### ComplexityMetrics

Code complexity metrics.

```python
@dataclass
class ComplexityMetrics:
    cyclomatic_complexity: float
    cognitive_complexity: float
    maintainability_index: float
    technical_debt_ratio: float
    halstead_metrics: HalsteadMetrics
```

### HalsteadMetrics

Halstead complexity metrics.

```python
@dataclass
class HalsteadMetrics:
    program_length: int
    vocabulary_size: int
    volume: float
    difficulty: float
    effort: float
```

### CodeInsights

Insights for a single code file.

```python
@dataclass
class CodeInsights:
    file_metrics: FileMetrics
    complexity_metrics: Optional[ComplexityMetrics]
    code_smells: List[str]
    duplications: List[Duplication]
```

### Duplication

Code duplication information.

```python
@dataclass
class Duplication:
    type: str  # function, class, block, etc.
    name: str  # Name of the duplicated element
    line: int  # Line number where duplication starts
    count: int  # Number of duplicates found
    locations: List[Dict[str, Any]]  # Detailed locations
```

### AnalysisReport

Complete analysis report.

```python
@dataclass
class AnalysisReport:
    project_path: Path
    timestamp: datetime
    total_files: int
    total_lines: int
    total_size: int
    language_distribution: Dict[Language, int]
    top_files: List[CodeInsights]
    recommendations: List[str]
```