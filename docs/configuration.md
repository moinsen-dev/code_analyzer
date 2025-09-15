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

# Language-specific settings
languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15
  javascript:
    max_line_length: 100
    complexity_threshold: 15

# Analysis rules
analysis:
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"
  
  complexity:
    include_docstrings: false
    count_assertions: true
  
  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

# AI configuration
# AI providers require API keys which should be set as environment variables:
# - OpenAI: OPENAI_API_KEY
# - Anthropic: ANTHROPIC_API_KEY
# - Google: GOOGLE_API_KEY
# - Ollama: No API key required (runs locally)
# - Qwen: No API key required (runs locally)
ai:
  # Enable AI-powered code suggestions
  enable_ai_suggestions: true
  
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
      enabled: true
    
    anthropic:
      # API key (can also be set via ANTHROPIC_API_KEY environment variable)
      # api_key: "your-anthropic-api-key"
      
      # Model to use
      model: "claude-3-haiku-20240307"
      
      # Whether this provider is enabled
      enabled: true
    
    google:
      # API key (can also be set via GOOGLE_API_KEY environment variable)
      # api_key: "your-google-api-key"
      
      # Model to use
      model: "gemini-pro"
      
      # Whether this provider is enabled
      enabled: true
    
    ollama:
      # Ollama doesn't require API keys
      
      # Model to use
      model: "llama2"
      
      # Base URL for Ollama (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true
    
    qwen:
      # Qwen doesn't require API keys for local installations
      
      # Model to use
      model: "qwen"
      
      # Base URL for Qwen (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true

# Output preferences
output:
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

# AI configuration
ai:
  # Enable AI-powered code suggestions
  enable_ai_suggestions: true
  
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
      enabled: true
    
    anthropic:
      # API key (can also be set via ANTHROPIC_API_KEY environment variable)
      # api_key: "your-anthropic-api-key"
      
      # Model to use
      model: "claude-3-haiku-20240307"
      
      # Whether this provider is enabled
      enabled: true
    
    google:
      # API key (can also be set via GOOGLE_API_KEY environment variable)
      # api_key: "your-google-api-key"
      
      # Model to use
      model: "gemini-pro"
      
      # Whether this provider is enabled
      enabled: true
    
    ollama:
      # Ollama doesn't require API keys
      
      # Model to use
      model: "llama2"
      
      # Base URL for Ollama (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true
    
    qwen:
      # Qwen doesn't require API keys for local installations
      
      # Model to use
      model: "qwen"
      
      # Base URL for Qwen (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true

## AI Configuration

The Refactoroscope includes advanced AI-powered code analysis and refactoring plan generation. The AI configuration allows you to customize how AI providers are used for code suggestions and refactoring plans.

### AI Provider Setup

AI providers require API keys which should be set as environment variables:
- **OpenAI**: `OPENAI_API_KEY`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **Google**: `GOOGLE_API_KEY`
- **Ollama**: No API key required (runs locally)
- **Qwen**: No API key required (runs locally)

### AI Configuration Options

The AI configuration section controls various aspects of AI-powered analysis:

- **enable_ai_suggestions**: Enable or disable AI-powered code suggestions
- **max_file_size**: Maximum file size to analyze with AI (in bytes)
- **cache_results**: Whether to cache AI analysis results for performance
- **cache_ttl**: Cache time-to-live in seconds
- **provider_preferences**: Preference order for AI providers
- **providers**: Detailed configuration for each AI provider

### Provider-Specific Configuration

Each AI provider can be configured with specific settings:

#### OpenAI
- **api_key**: Your OpenAI API key (can also be set via `OPENAI_API_KEY` environment variable)
- **model**: The model to use (e.g., "gpt-3.5-turbo", "gpt-4")
- **enabled**: Whether this provider is enabled

#### Anthropic
- **api_key**: Your Anthropic API key (can also be set via `ANTHROPIC_API_KEY` environment variable)
- **model**: The model to use (e.g., "claude-3-haiku-20240307", "claude-3-sonnet-20240229")
- **enabled**: Whether this provider is enabled

#### Google
- **api_key**: Your Google API key (can also be set via `GOOGLE_API_KEY` environment variable)
- **model**: The model to use (e.g., "gemini-pro", "gemini-1.5-pro")
- **enabled**: Whether this provider is enabled

#### Ollama
- **model**: The model to use (e.g., "llama2", "mistral")
- **base_url**: Base URL for Ollama (default is "http://localhost:11434")
- **enabled**: Whether this provider is enabled

#### Qwen
- **model**: The model to use (e.g., "qwen")
- **base_url**: Base URL for Qwen (default is "http://localhost:11434")
- **enabled**: Whether this provider is enabled

## Example Configurations

### Basic Configuration with AI

```yaml
version: 1.0

languages:
  python:
    max_line_length: 88
    complexity_threshold: 10

analysis:
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"
  
  complexity:
    include_docstrings: false
    count_assertions: true
  
  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

# AI configuration
ai:
  # Enable AI-powered code suggestions
  enable_ai_suggestions: true
  
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
      enabled: true

output:
  format: "terminal"  # terminal, json, html, csv
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
```
```