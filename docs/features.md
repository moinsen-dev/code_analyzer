---
layout: default
title: Features
---

# Features

## Core Analysis

### File Scanning
- Recursive directory scanning
- Respects `.gitignore` patterns at all directory levels
- Counts lines of code per file
- Displays file sizes in human-readable format
- Sorts results by line count

### Multi-Language Support
Support for 60+ programming languages:
- **Primary**: Python, JavaScript/TypeScript, Java, C#, C++/C, Go, Rust
- **Mobile**: Dart/Flutter, Swift, Kotlin
- **Web**: HTML, CSS/SCSS, Vue, React, Svelte
- **Scripting**: PHP, Ruby
- **Configuration**: YAML, JSON, TOML, XML
- **Data**: SQL, GraphQL
- **Documentation**: Markdown, reStructuredText

## Complexity Analysis

### Cyclomatic Complexity
Measures the number of linearly independent paths through code.

### Cognitive Complexity
Measures how difficult code is to understand, considering:
- Nesting levels
- Logical operators
- Control flow structures

### Halstead Metrics
Measures vocabulary size and program length:
- Program length
- Vocabulary size
- Volume
- Difficulty
- Effort

### Maintainability Index
Composite score (0-100) that estimates how maintainable the code is.

### Technical Debt Ratio
Estimates the technical debt in the codebase.

## Code Quality Analysis

### Code Smells Detection
Identifies common code smells:
- Long methods
- Large classes
- Complex conditionals
- Long parameter lists
- Deeply nested blocks

### Duplicate Code Detection
- AST-based duplicate code detection
- Identifies duplicate functions, classes, and control structures
- Reports duplicate counts and locations
- Clone type classification (exact, renamed, modified, semantic)
- Cross-file duplicate detection
- Similarity scoring

### Unused Code Detection
- AST-based static analysis for identifying dead code
- Detection of unused functions, classes, variables, and imports
- Confidence scoring for findings
- Cross-file usage tracking

### Unused File Detection
- Dependency graph analysis for identifying completely unused files
- Entry point identification
- Reachability analysis
- Confidence scoring for findings

## AI-Powered Analysis

### Code Quality Suggestions
- Intelligent insights on code readability
- Performance recommendations
- Potential bug detection
- Security issue identification

### Multi-Provider Support
- OpenAI (GPT models)
- Anthropic (Claude models)
- Google (Gemini models)
- Ollama (local models)
- Qwen (local models)

## Real-time Analysis

### File Watching
- Live monitoring of file changes
- Incremental analysis of modified files
- Terminal UI for real-time updates
- Configurable debounce delays

## Performance Optimizations

### Parallel Processing
- Multi-threaded file analysis
- Batch processing for large codebases
- Improved performance on multi-core systems

### Caching
- AST caching for faster re-analysis
- AI result caching
- Incremental analysis support

## Export Capabilities

### JSON Export
Structured JSON output for integration with other tools.

### HTML Reports
Interactive web-based reports with:
- Modern, responsive design
- Interactive charts
- Sortable tables
- Color-coded risk levels

### CSV Export
Tabular data export for spreadsheet analysis.

## Configuration

### Flexible Configuration
- YAML-based configuration files
- Language-specific settings
- Custom analysis thresholds
- Export preferences

### Ignore Patterns
- Configurable file ignore patterns
- Respects `.gitignore` rules
- Custom ignore rules in configuration

## Comparison

### Historical Analysis
- Compare analysis reports over time
- Track changes in codebase metrics
- Identify trends in code quality

## User Experience

### Rich Terminal UI
- Beautiful terminal output using Rich library
- Color-coded output
- Tabular data presentation
- Progress indicators

### Multiple Output Formats
- Terminal (default)
- JSON
- HTML
- CSV

## Integration

### CI/CD Integration
- GitHub Actions support
- GitLab CI support
- Other CI/CD platforms

### IDE Integration (Planned)
- VS Code extension
- IntelliJ plugin
- Other IDE integrations