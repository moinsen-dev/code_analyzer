# CI/CD Integration Guide

This guide explains how to integrate Refactoroscope into your CI/CD pipelines for automated code analysis.

## GitHub Actions

Refactoroscope provides built-in GitHub Actions workflows that you can use directly in your projects.

### Pre-built Workflows

1. **Code Analysis Workflow** (`refactoroscope.yml`): Runs code analysis on every push and pull request
2. **CI Workflow** (`ci.yml`): Runs tests, linting, and type checking
3. **Release Workflow** (`release.yml`): Automatically publishes to PyPI when tags are created
4. **Documentation Workflow** (`docs.yml`): Deploys documentation to GitHub Pages

### Using the Code Analysis Workflow

To use the built-in code analysis workflow in your project:

1. Copy the workflow file to your repository:
   ```bash
   mkdir -p .github/workflows
   cp .github/workflows/refactoroscope.yml .github/workflows/
   ```

2. Customize the workflow according to your project needs:
   ```yaml
   # In your .github/workflows/refactoroscope.yml
   - name: Run code analysis
     run: |
       refactoroscope analyze . --complexity --export json,html --export-dir ./reports
   ```

### Example Integration

Here's a complete example of integrating Refactoroscope into your GitHub Actions workflow:

```yaml
name: Code Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.13"

    - name: Install uv
      uses: astral-sh/setup-uv@v3

    - name: Install refactoroscope
      run: |
        uv pip install refactoroscope

    - name: Run code analysis
      run: |
        refactoroscope analyze . --complexity --export json,html --export-dir ./reports

    - name: Upload analysis reports
      uses: actions/upload-artifact@v4
      with:
        name: code-analysis-report
        path: ./reports/
        retention-days: 30
```

## GitLab CI/CD

For GitLab CI/CD, you can use the provided `.gitlab-ci.yml` configuration file.

### Using the GitLab CI Configuration

1. Copy the configuration file to your repository:
   ```bash
   cp .gitlab-ci.yml ./
   ```

2. Customize the configuration according to your project needs.

### Example GitLab CI Integration

```yaml
# In your .gitlab-ci.yml
analyze:
  stage: analyze
  image: python:3.13
  script:
    - pip install refactoroscope
    - refactoroscope analyze . --complexity --export json,html --export-dir ./reports
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
```

## Configuration Options

When integrating Refactoroscope into your CI/CD pipeline, you can customize the analysis with various options:

- `--complexity`: Include complexity analysis
- `--export json,html`: Export results in multiple formats
- `--export-dir ./reports`: Specify export directory
- `--ignore-patterns`: Ignore specific files or directories

Example with custom configuration:
```bash
refactoroscope analyze . \
  --complexity \
  --export json,html,csv \
  --export-dir ./reports \
  --ignore-patterns "tests/*" "docs/*"
```

## Failing Builds Based on Analysis Results

You can configure your CI/CD pipeline to fail builds based on analysis results:

```bash
# Example: Fail if any file has >1000 lines
refactoroscope analyze . --export json --export-dir ./reports
python -c "
import json
with open('./reports/report.json') as f:
    data = json.load(f)
for file in data['top_files']:
    if file['file_metrics']['lines_of_code'] > 1000:
        print(f'File {file[\"file_metrics\"][\"path\"]} has {file[\"file_metrics\"][\"lines_of_code\"]} lines, exceeding limit')
        exit(1)
"
```

## Best Practices

1. **Run on specific events**: Only run analysis on important branches or for specific events
2. **Archive reports**: Always archive analysis reports as artifacts for later review
3. **Set appropriate limits**: Configure complexity thresholds that match your team's standards
4. **Integrate with code review**: Use analysis results to inform code review processes
5. **Monitor trends**: Track code quality metrics over time to identify improvements or regressions