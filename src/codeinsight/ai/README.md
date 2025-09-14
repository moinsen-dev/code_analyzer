# AI-Powered Code Analysis in Refactoroscope

Refactoroscope includes AI-powered code quality suggestions that can help identify potential issues, suggest improvements, and provide insights about your codebase.

## Supported AI Providers

Refactoroscope supports multiple AI providers:

1. **OpenAI** (GPT models)
2. **Anthropic** (Claude models)
3. **Google** (Gemini models)
4. **Ollama** (Local models)
5. **Qwen** (Placeholder for future support)

## Configuration

To enable AI-powered analysis, you need to configure at least one AI provider in your `.refactoroscope.yml` file:

```yaml
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
  
  # Provider configurations
  providers:
    openai:
      # API key (can also be set via OPENAI_API_KEY environment variable)
      api_key: "your-openai-api-key"
      
      # Model to use
      model: "gpt-3.5-turbo"
      
      # Whether this provider is enabled
      enabled: true
```

### API Keys

For cloud-based providers (OpenAI, Anthropic, Google), you'll need API keys:

- **OpenAI**: Set `OPENAI_API_KEY` environment variable or configure in the YAML file
- **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable or configure in the YAML file
- **Google**: Set `GOOGLE_API_KEY` environment variable or configure in the YAML file

For Ollama, no API key is needed, but you must have Ollama running locally.

## Usage

### Command Line Interface

You can use AI analysis through several commands:

1. **AI-only analysis**:
   ```bash
   refactoroscope ai /path/to/code
   ```

2. **Integrated analysis** (enable AI during regular analysis):
   ```bash
   refactoroscope analyze /path/to/code --ai
   ```

3. **Real-time watching** with AI:
   ```bash
   refactoroscope watch /path/to/code --ai
   ```

### Provider Selection

Refactoroscope will automatically use the first available provider from your preference list. You can also specify a particular provider:

```bash
refactoroscope ai /path/to/code --provider openai
```

## Features

The AI analysis provides:

- Code quality suggestions
- Performance optimization recommendations
- Potential bug detection
- Security vulnerability identification
- Best practice recommendations
- Code readability improvements

## Cost Considerations

When using cloud-based AI providers, be aware of usage costs:

- **OpenAI**: ~$0.002 per 1K tokens for GPT-3.5
- **Anthropic**: ~$0.00025 per 1K tokens for Claude Haiku
- **Google**: ~$0.0005 per 1K tokens for Gemini Pro

To minimize costs:

1. Limit file sizes analyzed (default is 50KB)
2. Use local models like Ollama when possible
3. Enable caching to avoid re-analyzing unchanged files

## Performance

AI analysis performance varies by provider:

- **Local models (Ollama)**: Slower but no network latency, no costs
- **Cloud models**: Faster response but network-dependent

## Privacy

When using cloud-based providers, your code will be sent to their servers for analysis. For sensitive codebases, consider using local models like Ollama.