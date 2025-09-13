"""
Code complexity analyzer using Radon and other tools
"""
from pathlib import Path
from typing import Tuple, Optional
import ast

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

from codeinsight.models.metrics import ComplexityMetrics, Language


class ComplexityAnalyzer:
    """Analyzes code complexity using various metrics"""
    
    def analyze(self, file_path: Path, language: Language) -> Optional[ComplexityMetrics]:
        """
        Analyze complexity of a file
        
        Args:
            file_path: Path to the file
            language: Language of the file
            
        Returns:
            ComplexityMetrics or None if analysis failed
        """
        if not RADON_AVAILABLE:
            return None
            
        # Only analyze Python files for now
        if language != Language.PYTHON:
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Calculate cyclomatic complexity
            complexity_objects = cc_visit(content)
            cyclomatic = sum(obj.complexity for obj in complexity_objects) / max(len(complexity_objects), 1)
            
            # Calculate maintainability index
            mi_result = mi_visit(content, multi=True)
            maintainability = mi_result if isinstance(mi_result, (int, float)) else 0
            
            # Simple estimation of cognitive complexity and technical debt
            cognitive = self._estimate_cognitive_complexity(content)
            debt_ratio = self._estimate_technical_debt(content, cyclomatic)
            
            return ComplexityMetrics(
                cyclomatic_complexity=cyclomatic,
                cognitive_complexity=cognitive,
                maintainability_index=maintainability,
                technical_debt_ratio=debt_ratio
            )
            
        except Exception as e:
            print(f"Warning: Could not analyze complexity for {file_path}: {e}")
            return None
    
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
            if stripped.startswith(('if ', 'for ', 'while ', 'with ', 'try:', 'except')):
                nesting_level += 1
                cognitive += nesting_level  # Higher nesting increases cognitive complexity
            elif stripped.startswith('elif ') or stripped.startswith('else:'):
                cognitive += max(nesting_level - 1, 1)  # Else branches add complexity
            elif stripped in ('finally:', 'except:'):
                cognitive += max(nesting_level - 1, 1)
            
            # Decrease nesting for closing structures
            if stripped in ('endif', 'endfor', 'endwhile', 'endwith'):
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