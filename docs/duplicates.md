---
layout: default
title: Duplicate Code Detection
---

# Duplicate Code Detection

Refactoroscope provides advanced AST-based duplicate code detection with clone type classification to help identify redundant code in your project.

## How It Works

The duplicate code detection uses Abstract Syntax Tree (AST) analysis to identify similar code patterns while being resilient to superficial differences like variable names, whitespace, and comments.

## Clone Type Classification

The detection identifies different types of code clones:

- **Exact Clones** (Type-1): Identical code except for comments and whitespace
- **Renamed Clones** (Type-2): Syntactically identical with identifier renames
- **Modified Clones** (Type-3): Semantically similar with small modifications
- **Semantic Clones** (Type-4): Functionally equivalent but syntactically different

## Usage

To analyze for duplicate code:

```bash
uv run refactoroscope duplicates /path/to/your/project
```

### Analyzing for Specific Clone Types

To focus on exact duplicates only:

```bash
uv run refactoroscope duplicates /path/to/your/project --type exact
```

To focus on renamed clones:

```bash
uv run refactoroscope duplicates /path/to/your/project --type renamed
```

### Setting Similarity Thresholds

To find similar code with a minimum similarity threshold:

```bash
uv run refactoroscope duplicates /path/to/your/project --min-similarity 0.8
```

## Cross-File Detection

The duplicate detection works across different files in your project, identifying duplicated code patterns regardless of their location.

## Similarity Scoring

Results include quantitative similarity measures between code blocks (0.0 to 1.0), where:
- 1.0 indicates identical code
- 0.8-0.99 indicates highly similar code
- 0.5-0.79 indicates moderately similar code
- Below 0.5 indicates dissimilar code

## Performance Optimizations

The analysis uses caching and global indexing for efficient analysis of large codebases.

## Configuration

Duplicate detection can be configured through the `.refactoroscope.yml` configuration file:

```yaml
duplicates:
  # Minimum similarity threshold (0.0 to 1.0)
  min_similarity: 0.8
  
  # Clone types to detect
  clone_types:
    - "exact"
    - "renamed"
    - "modified"
    - "semantic"
  
  # Whether to include comments in comparison
  include_comments: false
  
  # Whether to include docstrings in comparison
  include_docstrings: false
  
  # Minimum number of lines for a clone
  min_lines: 3
  
  # Maximum number of lines for a clone
  max_lines: 100
  
  # Patterns to ignore
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
```

## Output Format

The duplicate detection output includes:

- File paths of duplicated code
- Line numbers of duplicated blocks
- Clone type classification
- Similarity scores
- Confidence levels

## Limitations

1. **Language Support**: Currently focused on Python code analysis
2. **Performance**: Analysis of very large codebases may take significant time
3. **False Positives**: Some similar code blocks may not be meaningful duplicates
4. **Memory Usage**: Large projects may require significant memory for analysis

## Best Practices

1. **Set Appropriate Thresholds**: Adjust similarity thresholds based on your needs
2. **Focus on Specific Types**: Use clone type filters to focus on specific kinds of duplication
3. **Review Results**: Always review duplicate findings before refactoring
4. **Incremental Analysis**: Use caching to speed up repeated analyses
5. **Combine with Other Tools**: Use duplicate detection alongside other code quality tools