---
layout: default
title: Configuration
---

The Refactoroscope can be configured using a `.refactoroscope.yml` file in your project root.

This file allows you to customize language-specific settings, analysis rules, and output preferences.

## Creating a Configuration File

To create a configuration file, run:

```bash
refactoroscope init
```

This will create a `.refactoroscope.yml` file with default settings.

To overwrite an existing configuration file:

```bash
uv run refactoroscope init --force
```

## Configuration File Structure

```yaml
version: 1.0

languages:
  # Language-specific settings
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15

analysis:
  # File patterns to ignore
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"
  
  # Complexity analysis options
  complexity:
    include_docstrings: false
    count_assertions: true
  
  # Analysis thresholds
  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000
  
  # Duplicate code detection
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
  
  # Unused code detection
  unused_code:
    # Confidence threshold for reporting (0.0 to 1.0)
    confidence_threshold: 0.5
    
    # Patterns to ignore
    ignore_patterns:
      - "test_*.py"
      - "*_test.py"
  
  # Unused file detection
  unused_files:
    # Confidence threshold for reporting (0.0 to 1.0)
    confidence_threshold: 0.5
    
    # Explicitly specify entry points
    entry_points:
      - "main.py"
      - "app.py"
      - "scripts/"
    
    # Patterns to ignore (in addition to global ignore patterns)
    ignore_patterns:
      - "test_*.py"
      - "*/migrations/*"
      - "*/fixtures/*"
    
    # Include/exclude specific directories
    include_dirs:
      - "src/"
    exclude_dirs:
      - "tests/"
      - "docs/"

# AI configuration
ai:
  # Enable AI-powered code suggestions
  enable_ai_suggestions: false
  
  # Maximum file size to analyze with AI (in bytes)
  max_file_size: 50000
  
  # Whether to cache AI analysis results
  cache_results: true
  
  # Cache time-to-live in seconds
  cache_ttl: 3600
  
  # Preference order for AI providers
  provider_preferences:
    - "openai"
    - "anthropic"
    - "google"
    - "ollama"
    - "qwen"
  
  # Provider configurations
  providers:
    openai:
      # API key (can also be set via OPENAI_API_KEY environment variable)
      # api_key: "your-openai-api-key"
      
      # Model to use
      model: "gpt-3.5-turbo"
      
      # Whether this provider is enabled
      enabled: false
    
    anthropic:
      # API key (can also be set via ANTHROPIC_API_KEY environment variable)
      # api_key: "your-anthropic-api-key"
      
      # Model to use
      model: "claude-3-haiku-20240307"
      
      # Whether this provider is enabled
      enabled: false
    
    google:
      # API key (can also be set via GOOGLE_API_KEY environment variable)
      # api_key: "your-google-api-key"
      
      # Model to use
      model: "gemini-pro"
      
      # Whether this provider is enabled
      enabled: false
    
    ollama:
      # Ollama doesn't require API keys
      
      # Model to use
      model: "llama2"
      
      # Base URL for Ollama (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: false
    
    qwen:
      # Qwen doesn't require API keys when using local Ollama
      
      # Model to use
      model: "qwen2"
      
      # Base URL for Qwen (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: false

# Watch configuration
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

output:
  # Output format
  format: "terminal"  # terminal, json, html, csv
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
```

## Language-Specific Settings

Configure settings for specific programming languages:

```yaml
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
  java:
    max_line_length: 100
    complexity_threshold: 12
```

## Analysis Configuration

### Ignore Patterns

Specify file patterns to ignore during analysis:

```yaml
analysis:
  ignore_patterns:
    # Generated files
    - "*.generated.*"
    - "*_pb2.py"
    # Build artifacts
    - "dist/"
    - "build/"
    - "*.min.js"
    # Dependencies
    - "node_modules/"
    - "vendor/"
    # Version control
    - ".git/"
    # IDE files
    - ".vscode/"
    - ".idea/"
```

### Complexity Options

Configure complexity analysis behavior:

```yaml
analysis:
  complexity:
    # Include docstrings in complexity calculations
    include_docstrings: false
    # Count assertions in complexity calculations
    count_assertions: true
```

### Thresholds

Set thresholds for code quality analysis:

```yaml
analysis:
  thresholds:
    # Maximum lines in a file before it's considered too long
    file_too_long: 500
    # Maximum complexity for a function before it's considered too complex
    function_too_complex: 20
    # Maximum members in a class before it's considered too large
    class_too_large: 1000
```

## Output Configuration

Configure output preferences:

```yaml
output:
  # Output format (terminal, json, html, csv)
  format: "terminal"
  # Theme for terminal output
  theme: "monokai"
  # Show recommendations in output
  show_recommendations: true
  # Default export directory
  export_path: "./reports"
```

## Environment Variables

The following environment variables can be used to configure the analyzer:

- `REFACTOROSCOPE_CONFIG_PATH`: Path to configuration file
- `REFACTOROSCOPE_EXPORT_PATH`: Default export directory
- `REFACTOROSCOPE_THEME`: Default terminal theme

## Example Configurations

### Web Development Project

```yaml
version: 1.0

languages:
  javascript:
    max_line_length: 100
    complexity_threshold: 15
  typescript:
    max_line_length: 100
    complexity_threshold: 15

analysis:
  ignore_patterns:
    - "node_modules/"
    - "dist/"
    - "build/"
    - "*.min.js"
    - "*.map"
  
  thresholds:
    file_too_long: 300
    function_too_complex: 15
    class_too_large: 500

output:
  format: "terminal"
  theme: "dracula"
  show_recommendations: true
  export_path: "./analysis"
```

### Python Project

```yaml
version: 1.0

languages:
  python:
    max_line_length: 88
    complexity_threshold: 10

analysis:
  ignore_patterns:
    - "__pycache__/"
    - "*.pyc"
    - "*.pyo"
    - ".pytest_cache/"
    - ".coverage"
  
  complexity:
    include_docstrings: false
    count_assertions: true
  
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

### Multi-Language Project

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
  java:
    max_line_length: 100
    complexity_threshold: 12

analysis:
  ignore_patterns:
    - "node_modules/"
    - "dist/"
    - "build/"
    - "__pycache__/"
    - "*.jar"
    - "*.class"
  
  thresholds:
    file_too_long: 400
    function_too_complex: 18
    class_too_large: 750

output:
  format: "terminal"
  theme: "github"
  show_recommendations: true
  export_path: "./analysis_reports"
```