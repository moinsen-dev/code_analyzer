---
layout: default
title: Real-time Watching
---

# Real-time Watching

Refactoroscope includes a real-time watching capability that monitors your codebase for changes and automatically re-analyzes affected files.

## How It Works

The watch feature uses the `watchdog` library to monitor file system events in your project directory. When changes are detected, Refactoroscope performs an incremental analysis of the modified files and updates the results in real-time.

## Usage

To start watching your project directory:

```bash
uv run refactoroscope watch .
```

You can also specify a specific directory to watch:

```bash
uv run refactoroscope watch /path/to/your/project
```

### Including Complexity Analysis

Complexity analysis is enabled by default when watching. To disable it:

```bash
uv run refactoroscope watch . --no-complexity
```

### AI-Powered Analysis

To enable AI-powered suggestions during watching:

```bash
uv run refactoroscope watch . --ai
```

Note that AI analysis is performed only on files that change, not on the entire codebase each time.

## Output Format

The watch command provides a terminal UI that updates in real-time with:

- Recently modified files
- Analysis results for changed files
- Summary statistics
- Any code smells or issues detected

## Configuration

You can configure the watching behavior through the `.refactoroscope.yml` configuration file:

```yaml
watch:
  # Debounce delay in seconds to prevent excessive analysis
  debounce_delay: 1.0
  
  # Whether to analyze on file creation events
  analyze_on_create: true
  
  # Whether to analyze on file modification events
  analyze_on_modify: true
  
  # Whether to analyze on file deletion events
  analyze_on_delete: true
  
  # Patterns to ignore (in addition to .gitignore)
  ignore_patterns:
    - "*.log"
    - "*.tmp"
    - ".DS_Store"
```

## Limitations

1. **Performance**: Continuous monitoring may consume system resources
2. **Large Projects**: For very large codebases, the initial analysis may take some time
3. **File Locks**: Files that are locked by other processes may not be analyzed immediately
4. **Network Drives**: Watching network drives may not work reliably on all platforms

## Best Practices

1. **Exclude Build Artifacts**: Add build artifacts and temporary files to ignore patterns
2. **Adjust Debounce Delay**: Increase the debounce delay for projects with frequent changes
3. **Use with Version Control**: The watch feature works best with version-controlled projects
4. **Monitor Resource Usage**: Keep an eye on CPU and memory usage during extended watching sessions