"""
Code complexity analyzer using Radon and other tools
"""

import ast
from pathlib import Path
from typing import Optional

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit

    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

try:
    from lizard import analyze as lizard_analyze

    LIZARD_AVAILABLE = True
except ImportError:
    LIZARD_AVAILABLE = False

from codeinsight.models.metrics import ComplexityMetrics, HalsteadMetrics, Language


class ComplexityAnalyzer:
    """Analyzes code complexity using various metrics"""

    def analyze(
        self, file_path: Path, language: Language
    ) -> Optional[ComplexityMetrics]:
        """
        Analyze complexity of a file

        Args:
            file_path: Path to the file
            language: Language of the file

        Returns:
            ComplexityMetrics or None if analysis failed
        """
        # Try to use Lizard for language-independent analysis first
        if LIZARD_AVAILABLE:
            try:
                return self._analyze_with_lizard(file_path, language)
            except Exception as e:
                print(
                    f"Warning: Could not analyze complexity with Lizard for {file_path}: {e}"
                )

        # Fallback to Radon for Python files
        if RADON_AVAILABLE and language == Language.PYTHON:
            try:
                return self._analyze_python_with_radon(file_path)
            except Exception as e:
                print(
                    f"Warning: Could not analyze complexity with Radon for {file_path}: {e}"
                )

        # If all methods fail, return None
        return None

    def _analyze_with_lizard(
        self, file_path: Path, language: Language
    ) -> Optional[ComplexityMetrics]:
        """
        Analyze complexity using Lizard for various languages

        Args:
            file_path: Path to the file
            language: Language of the file

        Returns:
            ComplexityMetrics or None if analysis failed
        """
        # Map our Language enum to lizard language names
        language_map = {
            Language.PYTHON: "python",
            Language.JAVASCRIPT: "javascript",
            Language.TYPESCRIPT: "typescript",
            Language.JAVA: "java",
            Language.CSHARP: "csharp",
            Language.CPP: "cpp",
            Language.GO: "go",
            Language.RUST: "rust",
            Language.DART: "dart",
            Language.SWIFT: "swift",
            Language.KOTLIN: "kotlin",
            Language.PHP: "php",
            Language.RUBY: "ruby",
        }

        # Check if we support this language with Lizard
        lizard_language = language_map.get(language)
        if not lizard_language:
            # For unsupported languages, we can't analyze complexity
            return None

        # Run Lizard analysis
        results = lizard_analyze([str(file_path)])

        # Process results
        total_ccn = 0
        total_functions = 0
        total_nloc = 0
        total_parameters = 0

        for result in results:
            if result:
                for func in result.function_list:
                    total_ccn += func.cyclomatic_complexity
                    total_nloc += func.nloc
                    total_parameters += func.parameter_count
                    total_functions += 1

        # Calculate averages
        avg_ccn = total_ccn / max(total_functions, 1) if total_functions > 0 else 0
        avg_nloc = total_nloc / max(total_functions, 1) if total_functions > 0 else 0
        avg_parameters = (
            total_parameters / max(total_functions, 1) if total_functions > 0 else 0
        )

        # Estimate maintainability index (simplified calculation)
        # Based on lines of code, cyclomatic complexity, and other factors
        maintainability = max(
            0, min(100, 171 - 5.2 * avg_ccn - 0.23 * avg_nloc - 16.2 * avg_parameters)
        )

        # Simple estimation of cognitive complexity and technical debt
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        cognitive = self._estimate_cognitive_complexity(content)
        debt_ratio = self._estimate_technical_debt(content, avg_ccn)

        # Calculate Halstead metrics (only for languages where we can parse AST)
        halstead = HalsteadMetrics()
        if language == Language.PYTHON:
            try:
                halstead = self._calculate_halstead_metrics(content)
            except Exception:
                pass  # Keep default halstead metrics if calculation fails - acceptable fallback

        return ComplexityMetrics(
            cyclomatic_complexity=avg_ccn,
            cognitive_complexity=cognitive,
            maintainability_index=maintainability,
            technical_debt_ratio=debt_ratio,
            halstead_metrics=halstead,
        )

    def _analyze_python_with_radon(
        self, file_path: Path
    ) -> Optional[ComplexityMetrics]:
        """
        Analyze Python complexity using Radon (fallback method)

        Args:
            file_path: Path to the Python file

        Returns:
            ComplexityMetrics or None if analysis failed
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Calculate cyclomatic complexity
        complexity_objects = cc_visit(content)
        cyclomatic = sum(obj.complexity for obj in complexity_objects) / max(
            len(complexity_objects), 1
        )

        # Calculate maintainability index
        mi_result = mi_visit(content, multi=True)
        maintainability = mi_result if isinstance(mi_result, (int, float)) else 0

        # Simple estimation of cognitive complexity and technical debt
        cognitive = self._estimate_cognitive_complexity(content)
        debt_ratio = self._estimate_technical_debt(content, cyclomatic)

        # Calculate Halstead metrics
        halstead = self._calculate_halstead_metrics(content)

        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            maintainability_index=maintainability,
            technical_debt_ratio=debt_ratio,
            halstead_metrics=halstead,
        )

    def _estimate_cognitive_complexity(self, content: str) -> float:
        """
        Estimate cognitive complexity based on code structure

        Args:
            content: File content

        Returns:
            Estimated cognitive complexity
        """
        # Simple estimation based on nesting and control structures
        lines = content.splitlines()
        nesting_level = 0
        cognitive = 0

        for line in lines:
            stripped = line.strip()

            # Increase nesting for control structures
            if stripped.startswith(
                ("if ", "for ", "while ", "with ", "try:", "except")
            ):
                nesting_level += 1
                cognitive += (
                    nesting_level  # Higher nesting increases cognitive complexity
                )
            elif stripped.startswith("elif ") or stripped.startswith("else:"):
                cognitive += max(nesting_level - 1, 1)  # Else branches add complexity
            elif stripped in ("finally:", "except:"):
                cognitive += max(nesting_level - 1, 1)

            # Decrease nesting for closing structures
            if stripped in ("endif", "endfor", "endwhile", "endwith"):
                nesting_level = max(0, nesting_level - 1)

        return cognitive

    def _estimate_technical_debt(self, content: str, cyclomatic: float) -> float:
        """
        Estimate technical debt ratio

        Args:
            content: File content
            cyclomatic: Cyclomatic complexity

        Returns:
            Estimated technical debt ratio
        """
        lines = content.splitlines()
        loc = len([line for line in lines if line.strip()])

        if loc == 0:
            return 0.0

        # Simple estimation: higher complexity and more lines = higher debt
        return min(cyclomatic / loc * 100, 100.0)

    def _calculate_halstead_metrics(self, content: str) -> HalsteadMetrics:
        """
        Calculate Halstead metrics for the code

        Args:
            content: File content

        Returns:
            HalsteadMetrics object
        """
        try:
            # Parse the AST
            tree = ast.parse(content)

            # Collect operators and operands
            operators = []
            operands = []

            # Walk the AST to collect operators and operands
            for node in ast.walk(tree):
                # Collect operators (keywords, operators, etc.)
                if isinstance(
                    node,
                    (
                        ast.If,
                        ast.For,
                        ast.While,
                        ast.FunctionDef,
                        ast.ClassDef,
                        ast.Try,
                        ast.With,
                    ),
                ):
                    operators.append(type(node).__name__)
                elif isinstance(node, (ast.Assign, ast.AugAssign)):
                    operators.append(type(node).__name__)
                elif isinstance(node, ast.BinOp):
                    operators.append(type(node.op).__name__)
                elif isinstance(node, ast.UnaryOp):
                    operators.append(type(node.op).__name__)
                elif isinstance(node, ast.Compare):
                    # Compare has multiple ops, collect each one
                    for op in node.ops:
                        operators.append(type(op).__name__)
                elif isinstance(node, ast.BoolOp):
                    operators.append(type(node.op).__name__)

                # Collect operands (names, constants, etc.)
                if isinstance(node, ast.Name):
                    operands.append(node.id)
                elif isinstance(node, ast.Constant):
                    operands.append(str(node.value))
                elif isinstance(node, (ast.Num, ast.Str)):  # For older Python versions
                    operands.append(str(node.n) if hasattr(node, "n") else str(node.s))

            # Calculate Halstead metrics
            operator_count = len(operators)
            operand_count = len(operands)

            # Unique operators and operands
            unique_operators = len(set(operators))
            unique_operands = len(set(operands))

            # Vocabulary size (n) = unique operators + unique operands
            vocabulary_size = unique_operators + unique_operands

            # Program length (N) = total operators + total operands
            program_length = operator_count + operand_count

            # Volume (V) = N * log2(n)
            import math

            if vocabulary_size > 0:
                volume = program_length * math.log2(vocabulary_size)
            else:
                volume = 0.0

            # Difficulty (D) = (unique operators / 2) * (operands / unique operands)
            if unique_operands > 0 and operand_count > 0:
                difficulty = (unique_operators / 2) * (operand_count / unique_operands)
            else:
                difficulty = 0.0

            # Effort (E) = D * V
            effort = difficulty * volume if volume > 0 else 0.0

            return HalsteadMetrics(
                program_length=program_length,
                vocabulary_size=vocabulary_size,
                volume=volume,
                difficulty=difficulty,
                effort=effort,
            )

        except Exception as e:
            # Return default metrics if calculation fails
            print(f"Warning: Could not calculate Halstead metrics: {e}")
            return HalsteadMetrics()
