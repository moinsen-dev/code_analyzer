# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-13

### Added
- Initial release of Code Insight Analyzer
- Code analysis capabilities with line counting and file size measurement
- Multi-language support for 60+ programming languages
- Code complexity analysis (Cyclomatic, Cognitive, Halstead metrics)
- Code smell detection using AST-based analysis
- Duplicate code detection
- Beautiful terminal output using Rich
- Export functionality to JSON, CSV, and HTML formats
- Configuration file support (.codeinsight.yml)
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