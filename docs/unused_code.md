# Unused Code Detection

Refactoroscope includes a powerful unused code detection feature that helps identify potentially dead code in your Python projects.

## How It Works

The unused code detection uses static analysis based on Python's Abstract Syntax Tree (AST) to:

1. Parse Python source files into ASTs
2. Track definitions of functions, classes, variables, and imports
3. Track usages of these definitions
4. Report definitions that have no corresponding usages

## Usage

To analyze your project for unused code, run:

```bash
uv run refactoroscope unused /path/to/your/project
```

This will scan all Python files in the specified directory and report any unused code elements.

## Output Format

The output shows:

- File path where unused code is found
- Type of unused element (function, class, variable, import)
- Name of the unused element
- Line number where it's defined
- Confidence level (higher confidence means more likely to be truly unused)

## Confidence Levels

Different types of code elements have different confidence levels:

- Imports: 90% confidence
- Functions and classes: 70% confidence
- Variables: 60% confidence

The confidence level helps you prioritize which findings to investigate first.

## Limitations

As with all static analysis tools, there are some limitations:

1. **Dynamic references**: Code that is referenced dynamically (e.g., through `getattr`) may be incorrectly flagged as unused
2. **Entry points**: Code that serves as an entry point but isn't called within the codebase may be flagged
3. **Framework code**: Code that integrates with frameworks may have false positives

## Best Practices

1. Review findings with high confidence first
2. Consider the context of your application when evaluating findings
3. Add truly necessary code that is flagged as unused to a whitelist or documentation
4. Use version control to track changes when removing unused code