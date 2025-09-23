---
layout: default
title: AI-Powered Analysis
---

# AI-Powered Analysis

Refactoroscope includes AI-powered code quality suggestions that provide intelligent insights on code readability, performance, potential bugs, and security issues. **Note: AI functionality is now integrated directly into the main `analyze` command rather than being a separate command.**

## How It Works

The AI analysis feature uses multiple AI providers to analyze your code and provide suggestions for improvement. The analysis is performed on a file-by-file basis, with each file being analyzed separately by the AI model. AI-generated suggestions are integrated into the existing code smell detection system.

## Supported AI Providers

Refactoroscope supports multiple AI providers:

1. **OpenAI**: Supports GPT models (GPT-3.5, GPT-4, etc.)
2. **Anthropic**: Supports Claude models
3. **Google**: Supports Gemini models
4. **Ollama**: Supports locally-run models (no API key required)
5. **Qwen**: Supports Qwen models

## Usage

To analyze your project with AI:

```bash
# Enable AI suggestions during regular analysis
uv run refactoroscope analyze /path/to/your/project --ai

# Enable AI suggestions during watching
uv run refactoroscope watch /path/to/your/project --ai
```

AI-generated suggestions will appear in the "Code Smells Detected" section of the analysis output.

## Configuration

AI functionality is configured in the `.refactoroscope.yml` configuration file. See the [Configuration Guide](configuration.md) for details.

To analyze with a specific AI provider:

```bash
uv run refactoroscope ai /path/to/your/project --provider openai
```

To enable AI suggestions during regular analysis:

```bash
uv run refactoroscope analyze . --ai
```

To enable AI suggestions during watching:

```bash
uv run refactoroscope watch . --ai
```

## Configuration

AI features are configured through the `.refactoroscope.yml` configuration file:

```yaml
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
      # Qwen doesn't require API keys when using local Ollama
      
      # Model to use
      model: "qwen2"
      
      # Base URL for Qwen (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true
```

## Environment Variables

For cloud-based providers, you can set API keys via environment variables:

- `OPENAI_API_KEY` for OpenAI
- `ANTHROPIC_API_KEY` for Anthropic
- `GOOGLE_API_KEY` for Google

## Output Format

AI analysis results are integrated into the regular analysis output and include:

- Code quality suggestions
- Performance recommendations
- Potential bug detection
- Security issue identification
- Readability improvements

Each AI suggestion includes a confidence level and a detailed explanation.

## Limitations

1. **API Costs**: Cloud-based AI providers may incur costs based on usage
2. **Privacy**: Code is sent to external AI providers (except for local providers like Ollama)
3. **Response Time**: AI analysis may take longer than static analysis
4. **Accuracy**: AI suggestions may not always be applicable to your specific context

## Best Practices

1. **Start with Local Models**: Use Ollama or similar local providers for initial testing
2. **Set File Size Limits**: Configure appropriate file size limits to control costs
3. **Use Caching**: Enable caching to avoid re-analyzing unchanged files
4. **Review Suggestions**: Always review AI suggestions before implementing them
5. **Configure Preferences**: Set up provider preferences based on your needs and budget