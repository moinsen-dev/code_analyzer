# Unused Code Detection in Python Projects

This document outlines various approaches for detecting unused code in Python projects, with a focus on practical implementation strategies that could be integrated into the Refactoroscope architecture.

## 1. Static Analysis Approaches Using AST

### Overview
Static analysis using Abstract Syntax Trees (AST) is the most common approach for detecting unused code in Python. Tools parse Python source code into ASTs without executing it, then analyze the tree structure to identify unused elements.

### Implementation Strategy

1. **AST Parsing**: Use Python's built-in `ast` module to parse source files
2. **Name Tracking**: Track definitions and usages of names throughout the codebase
3. **Scope Analysis**: Handle different scopes (global, local, class) appropriately
4. **Reporting**: Flag defined objects that have no corresponding references

### Example Implementation Pattern
```python
import ast

class UnusedCodeDetector(ast.NodeVisitor):
    def __init__(self):
        self.defined_names = set()
        self.used_names = set()
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_names.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)
        
    def get_unused_names(self):
        return self.defined_names - self.used_names
```

### Advantages
- Fast execution without running code
- Safe analysis of modules with side effects
- No runtime dependencies

### Limitations
- May miss dynamically referenced code
- False positives with complex dynamic behavior
- Limited understanding of runtime behavior

## 2. Symbol Usage Tracking

### Overview
Symbol usage tracking focuses on recording where symbols (variables, functions, classes) are defined and where they are used. This approach builds upon AST analysis but with more sophisticated tracking.

### Implementation Strategy

1. **Symbol Table Construction**: Build symbol tables for each scope
2. **Reference Tracking**: Track all references to symbols
3. **Lifetime Analysis**: Determine when symbols go out of scope
4. **Cross-Module Analysis**: Handle imports and exports between modules

### Example Implementation Pattern
```python
class SymbolTracker:
    def __init__(self):
        self.symbols = {}
        self.references = {}
        
    def define_symbol(self, name, location):
        if name not in self.symbols:
            self.symbols[name] = []
        self.symbols[name].append(location)
        
    def reference_symbol(self, name, location):
        if name not in self.references:
            self.references[name] = []
        self.references[name].append(location)
        
    def get_unused_symbols(self):
        unused = []
        for name, definitions in self.symbols.items():
            if name not in self.references:
                unused.extend(definitions)
        return unused
```

### Advantages
- More accurate than simple name tracking
- Handles scoping correctly
- Can track complex symbol relationships

### Limitations
- Complex implementation for proper scoping
- Still limited by static analysis constraints
- Difficult to handle dynamic symbol creation

## 3. Import/Export Analysis

### Overview
Import/export analysis focuses specifically on identifying unused imports and exports between modules. This is a specialized form of symbol tracking that focuses on inter-module dependencies.

### Implementation Strategy

1. **Import Tracking**: Record all imports from each module
2. **Usage Analysis**: Track which imported symbols are actually used
3. **Export Identification**: Identify what symbols each module exports
4. **Dependency Mapping**: Build a dependency graph of modules

### Example Implementation Pattern
```python
class ImportAnalyzer:
    def __init__(self):
        self.imports = {}  # module -> {symbol: location}
        self.symbol_usage = {}  # symbol -> [usage_locations]
        
    def analyze_imports(self, file_path):
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.record_import(file_path, alias.name, node.lineno)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    full_name = f"{node.module}.{alias.name}"
                    self.record_import(file_path, full_name, node.lineno)
                    
    def record_import(self, file_path, symbol, line):
        if file_path not in self.imports:
            self.imports[file_path] = {}
        self.imports[file_path][symbol] = line
```

### Advantages
- Highly accurate for import-related issues
- Can identify unused modules entirely
- Good for dependency analysis

### Limitations
- Doesn't address intra-module unused code
- May miss dynamic imports
- Limited scope of analysis

## 4. Cross-File Dependency Analysis

### Overview
Cross-file dependency analysis extends symbol tracking to work across multiple files, building a comprehensive view of how symbols are used throughout a project.

### Implementation Strategy

1. **Project-Wide Analysis**: Analyze all files in a project together
2. **Dependency Graph Construction**: Build a graph of symbol dependencies
3. **Reachability Analysis**: Determine which symbols are reachable from entry points
4. **Dead Code Identification**: Identify symbols that are not reachable

### Example Implementation Pattern
```python
class CrossFileAnalyzer:
    def __init__(self):
        self.symbol_definitions = {}  # symbol -> {file: location}
        self.symbol_references = {}   # symbol -> [locations]
        self.dependencies = {}         # file -> [dependent_files]
        
    def analyze_project(self, project_path):
        # Analyze all Python files
        for file_path in self._find_python_files(project_path):
            self._analyze_file(file_path)
            
        # Build dependency graph
        self._build_dependency_graph()
        
        # Identify unused code
        return self._find_unused_symbols()
        
    def _analyze_file(self, file_path):
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
            
        # Process definitions and references
        visitor = SymbolVisitor(file_path)
        visitor.visit(tree)
        
        # Update project-wide tracking
        self._update_symbol_tracking(file_path, visitor)
```

### Advantages
- Comprehensive project-wide view
- Can identify completely unused modules
- Good for refactoring guidance

### Limitations
- Computationally expensive
- Complex to implement correctly
- May require configuration for entry points

## 5. Third-Party Tools Integration

### Popular Tools

#### Vulture
- **Methodology**: AST-based analysis with name tracking
- **Confidence Levels**: Assigns confidence values to findings
- **Special Features**: Detects unreachable code, unused attributes
- **Integration Approach**: Parse Vulture's output or use its analysis engine

#### Pyflakes
- **Methodology**: AST-based symbol tracking with scope analysis
- **Strengths**: Fast, safe (doesn't execute code)
- **Limitations**: Limited to syntactic analysis
- **Integration Approach**: Leverage pyflakes' robust AST analysis

#### Unimport
- **Methodology**: Specialized import analysis
- **Strengths**: Accurate detection of unused imports
- **Integration Approach**: Focus on import-related analysis

### Integration Strategy

1. **Wrapper Approach**: Create wrappers around existing tools
2. **Library Integration**: Directly use tool libraries when available
3. **Output Parsing**: Parse and standardize output from external tools
4. **Hybrid Analysis**: Combine multiple tools for comprehensive coverage

## 6. Best Practices for Accuracy vs. False Positives

### Accuracy Enhancement Techniques

1. **Context-Aware Analysis**: Consider symbol context when determining usage
2. **Entry Point Specification**: Allow users to specify project entry points
3. **Configuration Support**: Provide configuration for ignoring specific patterns
4. **Whitelist Support**: Allow users to whitelist known false positives

### False Positive Reduction Techniques

1. **Confidence Scoring**: Assign confidence levels to findings
2. **Pattern Recognition**: Identify common false positive patterns
3. **Dynamic Analysis Hints**: Use simple runtime checks to validate findings
4. **User Feedback Loop**: Allow users to mark findings as valid/invalid

### Example Confidence Scoring
```python
class ConfidenceScorer:
    def __init__(self):
        self.rules = {
            'function_args': 100,
            'imports': 90,
            'attributes': 60,
            'functions': 60,
            'classes': 60,
            'variables': 60
        }
        
    def score_unused_item(self, item_type, context):
        base_score = self.rules.get(item_type, 50)
        
        # Adjust based on context
        if context.get('public_api'):
            return base_score * 0.7  # Lower confidence for public APIs
            
        return base_score
```

## Integration with Refactoroscope Architecture

### Implementation Approach

1. **Analyzer Module**: Create a new analyzer following the existing pattern
2. **Model Integration**: Add unused code findings to the existing data models
3. **CLI Command**: Add a new CLI command for unused code analysis
4. **Configuration**: Add configuration options for unused code detection

### Proposed Implementation Steps

1. **Create Analyzer Module**:
   ```python
   # src/codeinsight/analyzers/unused_code.py
   class UnusedCodeAnalyzer:
       def analyze(self, file_path: Path, language: Language) -> List[str]:
           # Implementation here
   ```

2. **Update Models**:
   ```python
   # src/codeinsight/models/metrics.py
   @dataclass
   class CodeInsights:
       # ... existing fields
       unused_code: List[str] = field(default_factory=list)
   ```

3. **Integrate with Scanner**:
   ```python
   # src/codeinsight/scanner.py
   def _analyze_file_parallel(self, file_path: Path, root_path: Path, include_complexity: bool):
       # ... existing code
       unused_code = self.unused_code_analyzer.analyze(file_path, file_metrics.language)
       if unused_code:
           insight.unused_code = unused_code
   ```

4. **Add CLI Command**:
   ```python
   # src/codeinsight/cli.py
   @app.command()
   def unused(path: Path = typer.Argument(..., help="Path to analyze")):
       # Implementation here
   ```

This approach would maintain consistency with the existing Refactoroscope architecture while adding comprehensive unused code detection capabilities.