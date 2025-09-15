---
layout: default
title: Examples
---

# Examples

## Basic Analysis

### Simple Project Analysis

```bash
uv run refactoroscope analyze .
```

Output:
```
╭──────────────────────────────────╮
│ Refactoroscope v1.0                     │
│ Project: examples/sample_project │
╰──────────────────────────────────╯

📊 Analysis Summary
──────────────────
  Total Files:                                             6  
  Lines of Code:                                         163  
  Total Size:                                    5,193 bytes  
  Languages:        markdown (33%), python (33%), yaml (17%)  

📁 Top Files by Line Count
────────────────────────────
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┓
┃ File             ┃ Lines ┃        Size ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━┩
│ smelly.py        │    67 │ 2,161 bytes │
│ calculator.py    │    44 │ 1,749 bytes │
│ .refactoroscope.yml │    30 │   715 bytes │
│ greeter.js       │    18 │   466 bytes │
│ .gitignore       │     3 │    18 bytes │
│ README.md        │     1 │    84 bytes │
└──────────────────┴───────┴─────────────┘
```

## Complexity Analysis

### With Complexity Metrics

```bash
uv run refactoroscope analyze . --complexity
```

Output:
```
🔥 Complexity Hotspots (Top 5)
────────────────────────────────────
┏━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ File          ┃ Lines ┃ Complexity ┃ Risk Level ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ smelly.py     │    67 │        2.8 │  🟢 Good   │
│ calculator.py │    44 │        1.4 │  🟢 Good   │
└───────────────┴───────┴────────────┴────────────┘

💡 Code Smells Detected
────────────────────────
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File      ┃ Smell                                                    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ smelly.py │ Long method 'long_method' with 27 statements             │
│ smelly.py │ Complex conditional with 5 conditions                    │
│ smelly.py │ Function 'method_with_too_many_params' with 8 parameters │
│ smelly.py │ Function 'complex_conditional' with 6 parameters         │
│ smelly.py │ Deeply nested block (depth 5)                            │
│ smelly.py │ Deeply nested block (depth 6)                            │
└───────────┴──────────────────────────────────────────────────────────┘
```

## Export Examples

### JSON Export

```bash
uv run refactoroscope analyze . --export json --export-dir ./reports
```

Generated JSON structure:
```json
{
  "project_path": "examples/sample_project",
  "timestamp": "2025-09-13T15:14:15.119566",
  "total_files": 7,
  "total_lines": 251,
  "total_size": 8335,
  "language_distribution": {
    "yaml": 1,
    "markdown": 2,
    "python": 2,
    "javascript": 2
  },
  "top_files": [
    {
      "file_metrics": {
        "path": "examples/sample_project/complex.js",
        "relative_path": "complex.js",
        "language": "javascript",
        "lines_of_code": 88,
        "blank_lines": 7,
        "comment_lines": 14,
        "size_bytes": 3142,
        "last_modified": "2025-09-13T12:45:30"
      },
      "complexity_metrics": {
        "cyclomatic_complexity": 2.6,
        "cognitive_complexity": 1.8,
        "maintainability_index": 78.5,
        "technical_debt_ratio": 3.2,
        "halstead_metrics": {
          "program_length": 156,
          "vocabulary_size": 42,
          "volume": 842.1,
          "difficulty": 18.9,
          "effort": 15915.7
        }
      }
    }
  ]
}
```

### HTML Export

```bash
uv run refactoroscope analyze . --export html --export-dir ./reports
```

Generates a comprehensive HTML report with:
- Interactive charts
- Sortable tables
- Color-coded risk levels
- Detailed metrics for each file

## Comparison Examples

### Comparing Two Analyses

```bash
uv run refactoroscope compare reports/2025-01-01.json reports/2025-01-15.json
```

Output:
```
                     Summary Comparison                      
┏━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric      ┃ Report 1 ┃ Report 2 ┃ Difference ┃ Change % ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Files │        5 │        5 │         +0 │    +0.0% │
│ Total Lines │       87 │       96 │         +9 │   +10.3% │
│ Total Size  │    2,681 │    3,032 │       +351 │   +13.1% │
└─────────────┴──────────┴──────────┴────────────┴──────────┘

File Changes:
  ~ 1 changed files

Complexity Changes:
  1 files with complexity changes
```

## Configuration Examples

### Basic Configuration

Create a `.refactoroscope.yml` file:

```yaml
version: 1.0

languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15

analysis:
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
  
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

### Advanced Configuration

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

analysis:
  ignore_patterns:
    - "*.min.js"
    - "node_modules/"
    - "*.lock"
    - "dist/"
    - "build/"
  
  complexity:
    include_docstrings: false
    count_assertions: true
  
  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

output:
  format: "terminal"
  theme: "dracula"
  show_recommendations: true
  export_path: "./analysis_reports"
```