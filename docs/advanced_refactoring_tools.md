---
layout: default
title: Advanced Refactoring Tools
---

# Advanced Refactoring Tools

Refactoroscope now includes advanced refactoring tools that provide AI-powered refactoring plan generation and tech stack analysis with integrated tool execution.

## Tech Stack Detection

Refactoroscope can automatically detect technology stacks in your project folders:

- **Python**: Detects projects with `requirements.txt`, `setup.py`, `pyproject.toml`, or `.py` files
- **JavaScript/TypeScript**: Detects projects with `package.json`, `.js`/`.jsx`/`.ts`/`.tsx` files
- **Java/Kotlin**: Detects projects with `pom.xml`, `build.gradle`, or `.java`/`.kt` files
- **Flutter/Dart**: Detects projects with `pubspec.yaml` or `.dart` files
- **Go**: Detects projects with `go.mod` or `.go` files
- **Rust**: Detects projects with `Cargo.toml` or `.rs` files
- **Ruby**: Detects projects with `Gemfile` or `.rb` files
- **PHP**: Detects projects with `composer.json` or `.php` files

## Integrated Tool Execution

Once tech stacks are detected, Refactoroscope automatically runs the appropriate tools:

### Python
- **Linters**: `ruff check .`, `flake8 .`
- **Formatters**: `black --check .`, `isort --check-only .`
- **Type Checkers**: `mypy .`

### JavaScript/TypeScript
- **Linters**: `eslint .`
- **Formatters**: `prettier --check .`

### Flutter
- **Linters**: `flutter analyze`
- **Formatters**: `dart format --output=none --set-exit-if-changed .`

### Go
- **Linters**: `golint ./...`, `go vet ./...`
- **Formatters**: `gofmt -l .`
- **Type Checkers**: `go build ./...`

### Rust
- **Linters**: `cargo clippy`
- **Formatters**: `cargo fmt -- --check`
- **Type Checkers**: `cargo check`

## Outdated Package Detection

Refactoroscope checks for outdated packages in each tech stack:

- **Python**: Uses `pip list --outdated`
- **JavaScript/TypeScript**: Uses `npm outdated --json`
- **Flutter**: Uses `flutter pub outdated --json`
- **Rust**: Uses `cargo update --dry-run`

## AI-Powered Refactoring Plan Generation

The `refactor-plan` command generates comprehensive, AI-based refactoring plans with the following structure:

### Phased Approach
1. **Phase 1: Critical Issues (High Priority)** - Security vulnerabilities, critical bugs, major performance issues
2. **Phase 2: Code Quality Improvements (Medium Priority)** - Maintainability, readability, technical debt reduction
3. **Phase 3: Architecture Enhancements (Low Priority)** - Long-term architectural improvements and scalability

### Detailed Recommendations
- **Complexity Reduction** - Address functions/classes with high cyclomatic complexity
- **Duplicate Code Elimination** - Merge or refactor duplicated code sections
- **Code Smell Resolution** - Fix identified code smells like long methods, large classes, etc.
- **Unused Code Removal** - Remove dead code that is never used
- **Performance Optimizations** - Address any performance bottlenecks

### Implementation Timeline
Suggested timeline with milestones and resource allocation.

### Risk Assessment
Potential risks and mitigation strategies for each phase.

### Success Metrics
How to measure the success of the refactoring efforts.

## Usage Examples

### Tech Stack Analysis and Tool Execution

```bash
# Analyze current directory and run appropriate tools for detected tech stacks
refactoroscope analyze . --check

# This will:
# 1. Detect technology stacks in all subfolders
# 2. Run appropriate linters, formatters, and type checkers
# 3. Check for outdated packages
# 4. Display results in terminal
```

### AI-Powered Refactoring Plan Generation

```bash
# Generate an AI-based refactoring plan for your project
refactoroscope refactor-plan .

# Generate refactoring plan with specific AI provider
refactoroscope refactor-plan . --provider openai

# Save refactoring plan to specific file
refactoroscope refactor-plan . --output my_refactoring_plan.md
```

## Configuration

The advanced refactoring tools can be configured in your `.refactoroscope.yml` file:

```yaml
# Advanced refactoring configuration
refactoring:
  # Enable tech stack detection and tool execution
  enable_tech_stack_check: true
  
  # Enable AI-powered refactoring plan generation
  enable_ai_refactor_plan: true
  
  # AI provider for refactoring plan generation
  ai_provider: "openai"
  
  # Output file for refactoring plan
  refactor_plan_output: "refactor_plan.md"
  
  # Timeout for tool execution (seconds)
  tool_timeout: 300
  
  # Whether to check for outdated packages
  check_outdated_packages: true
```

## Requirements

The advanced refactoring tools require the following dependencies to be installed in your system:

- **Python tools**: `ruff`, `flake8`, `black`, `isort`, `mypy`
- **JavaScript/TypeScript tools**: `eslint`, `prettier`
- **Flutter tools**: `flutter` SDK
- **Go tools**: `golint`, standard Go toolchain
- **Rust tools**: `cargo` toolchain

Make sure these tools are available in your system PATH for Refactoroscope to execute them.