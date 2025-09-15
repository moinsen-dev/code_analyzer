---
layout: default
title: Use Cases
---

# Typical Use Cases

Here are common scenarios where Refactoroscope can help you improve your codebase:

## 1. Getting Started - Quick Project Overview

When you join a new project or want to understand an existing codebase:

```bash
refactoroscope analyze .
```

This gives you an immediate overview of:
- How many files and lines of code you're dealing with
- Which languages are used in the project
- File sizes to identify potentially large files

## 2. Code Quality Assessment

Before a major release, assess the technical health of your codebase:

```bash
refactoroscope analyze . --complexity --export html --export-dir ./reports
```

This command:
- Analyzes code complexity metrics
- Generates an HTML report for easy sharing with your team
- Identifies functions and files with high complexity that might need refactoring

## 3. Identifying Duplicate Code

Find duplicated code that could be consolidated:

```bash
refactoroscope duplicates src/
```

This helps you:
- Reduce maintenance burden by eliminating redundant code
- Improve consistency across your codebase
- Identify opportunities for creating reusable components

## 4. Finding Unused Code

Clean up your codebase by identifying dead code:

```bash
refactoroscope unused src/
```

This identifies:
- Unused functions and methods
- Unused variables and imports
- Dead code that can be safely removed

## 5. Detecting Unused Files

Identify entire files that are no longer used in your project:

```bash
refactoroscope unused-files src/
```

This helps you:
- Remove obsolete files that are no longer imported anywhere
- Reduce project clutter and improve build times
- Clean up legacy code that's no longer needed

## 6. Continuous Integration Integration

Integrate Refactoroscope into your CI pipeline to automatically analyze code quality:

```yaml
# In your GitHub Actions workflow
- name: Analyze code quality
  run: |
    pip install refactoroscope
    refactoroscope analyze . --complexity --export json --export-dir ./reports
```

## 7. Monitoring Code Changes

During development, watch your code for changes and get real-time analysis:

```bash
refactoroscope watch .
```

This continuously monitors your files and provides immediate feedback on:
- New code complexity
- File size changes
- Code quality trends

## 8. Comparing Code Quality Over Time

Track improvements or degradations in your codebase over time:

```bash
# First analysis
refactoroscope analyze . --export json --export-dir ./reports
# ... some time later, after making changes ...
refactoroscope analyze . --export json --export-dir ./reports
# Compare the two analyses
refactoroscope compare reports/report1.json reports/report2.json
```

This approach helps you:
- Measure the impact of refactoring efforts
- Catch quality regressions before they're merged
- Track technical debt trends over time

## 9. Getting AI-Powered Code Suggestions

Get intelligent feedback on your code quality:

```bash
refactoroscope ai src/ --provider openai
```

This provides:
- Actionable suggestions for improving code readability
- Identification of potential performance bottlenecks
- Security vulnerability assessments
- Best practice recommendations

## 10. Configuration for Team Standards

Create a `.refactoroscope.yml` configuration file to enforce team coding standards:

```yaml
version: 1.0

analysis:
  thresholds:
    file_too_long: 500      # Flag files with more than 500 lines
    function_too_complex: 15 # Flag functions with complexity over 15
    
  ignore_patterns:
    - "tests/"              # Ignore test files
    - "migrations/"         # Ignore database migrations
    - "*.min.js"            # Ignore minified JavaScript

output:
  show_recommendations: true
  export_path: "./reports"
```

Then run analyses with your team's standards:

```bash
refactoroscope analyze .
```

These use cases demonstrate how Refactoroscope can be integrated into different phases of your development workflow, from initial exploration to ongoing maintenance and quality assurance.