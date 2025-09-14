# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-09-14

### Added
- Unused file detection using dependency graph analysis
- New `unused-files` CLI command for identifying completely unused files
- Support for detecting unused Python files through import dependency analysis
- Confidence scoring for unused file findings
- Comprehensive documentation for unused file detection
- Tests for unused file detection functionality

## [0.3.2] - 2025-09-14

### Added
- Unused code detection using AST-based static analysis
- New `unused` CLI command for identifying dead code
- Support for detecting unused functions, classes, variables, and imports
- Confidence scoring for unused code findings
- Comprehensive documentation for unused code detection
- Tests for unused code detection functionality

## [0.3.1] - 2025-09-14

### Changed
- Made complexity analysis enabled by default for all commands
- Added `--no-complexity` and `-C` flags to disable complexity analysis
- Updated version number to 0.3.1 across all configuration files
- Enhanced documentation to reflect new default behavior

## [0.3.0] - 2025-09-14

### Added
- Advanced AST-based duplicate code detection with clone type classification
- Cross-file duplicate detection capability
- Clone type classification (exact, renamed, modified, semantic)
- Similarity scoring for duplicate code blocks
- Global AST indexing system for efficient cross-file comparison
- Performance optimizations with caching and incremental analysis
- Dedicated `duplicates` CLI command for focused duplicate analysis
- Enhanced Duplication model with clone type and similarity information
- Comprehensive tests for advanced duplicate detection functionality

### Changed
- Enhanced existing duplicate detection with advanced AST normalization
- Improved CLI with new options for duplicate code analysis
- Updated documentation with advanced duplicate detection features

## [0.2.1] - 2025-09-14

### Added
- Real-time file watching capability with `watch` command
- Live code analysis updates when files change
- File system monitoring using watchdog library
- Debounced analysis to prevent excessive CPU usage
- Terminal UI for live updates

## [0.2.0] - 2025-09-13

### Added
- CI/CD integration support for GitHub Actions and GitLab CI
- Pre-built GitHub Actions workflow for code analysis
- GitLab CI configuration template
- GitHub Action for direct use in workflows
- CI/CD integration documentation
- Dockerfile for GitHub Action
- Enhanced CI workflow with code quality checks and benchmarking
- CI/CD badges in README

### Changed
- Updated package name from "CodeMRI" to "refactoroscope"
- Updated version to 0.2.0 in pyproject.toml and setup.py
- Enhanced existing CI workflow with additional jobs

## [0.1.0] - 2025-09-13

### Added
- Initial release of Code Analyzer
- Code analysis capabilities with line counting and file size measurement
- Multi-language support for 60+ programming languages
- Code complexity analysis (Cyclomatic, Cognitive, Halstead metrics)
- Code smell detection using AST-based analysis
- Duplicate code detection
- Beautiful terminal output using Rich
- Export functionality to JSON, CSV, and HTML formats
- Configuration file support (.refactoroscope.yml)
- GitIgnore pattern respect at all directory levels
- Performance optimizations with parallel processing
- Comprehensive test suite with >90% coverage
- Strict type checking with mypy

### Changed
- Fixed critical bug in CLI display causing UnboundLocalError
- Improved error handling for missing complexity metrics
- Enhanced package metadata for PyPI release

### Fixed
- Type annotation issues throughout the codebase
- Variable scoping issues in terminal display functions
- Build system configuration for proper packaging