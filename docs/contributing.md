---
layout: default
title: Contributing
---

# Contributing

We welcome contributions to the Refactoroscope project! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/code-insight-analyzer.git
   cd code-insight-analyzer
   ```
3. Install dependencies:
   ```bash
   uv sync
   ```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Development branch for next release
- Feature branches: Create from `develop` for new features
- Hotfix branches: Create from `main` for urgent fixes

### Code Style

We follow these style guides:
- Python: [PEP 8](https://pep8.org/)
- Formatting: [Black](https://github.com/psf/black)
- Import sorting: [isort](https://pycqa.github.io/isort/)
- Type checking: [mypy](http://mypy-lang.org/)

Run the following commands to ensure code quality:

```bash
# Format code
uv run black src/

# Sort imports
uv run isort src/

# Lint code
uv run ruff check src/

# Type check
uv run mypy src/
```

### Testing

Run tests with:

```bash
uv run pytest
```

For test coverage:

```bash
uv run pytest --cov=src/
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[body]

[footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

## Submitting Changes

1. Create a feature branch from `develop`
2. Make your changes
3. Add tests if applicable
4. Update documentation if needed
5. Run all checks and tests
6. Commit your changes
7. Push to your fork
8. Create a pull request to `develop`

## Code Review Process

All submissions require review. We use GitHub pull requests for this process.

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation updates
- Adherence to project architecture
- Performance considerations

## Reporting Issues

Use GitHub Issues to report bugs or request features:
- Use a clear and descriptive title
- Include steps to reproduce for bugs
- Provide expected and actual behavior
- Include environment details (OS, Python version, etc.)

## Community

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and best practices
- Welcome newcomers