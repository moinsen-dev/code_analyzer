"""
Refactor Plan Generator for Refactoroscope
Generates AI-based refactoring plans based on code analysis
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from codeinsight.scanner import Scanner


class RefactorPlanGenerator:
    """Generates AI-based refactoring plans"""

    def __init__(self, ai_provider: Any) -> None:
        self.ai_provider = ai_provider

    def generate_plan(self, path: Path) -> str:
        """
        Generate a refactoring plan for the given path

        Args:
            path: Path to analyze

        Returns:
            Markdown formatted refactoring plan
        """
        # Run initial analysis
        scanner = Scanner(path, enable_duplicates=True, enable_ai=True)
        report = scanner.analyze(path, include_complexity=True)

        # Run duplicate code analysis
        # Duplicate analysis is now part of the regular analysis process
        # We'll extract duplicates from the report

        # Generate plan using AI
        # Extract duplicates from all code insights in the report
        all_duplications = []
        for insight in report.top_files:
            if hasattr(insight, "duplications") and insight.duplications:
                all_duplications.extend(insight.duplications)

        plan_data = {
            "analysis_report": report.to_dict(),
            "duplicates": [d.__dict__ for d in all_duplications],
        }

        # Create prompt for AI
        prompt = self._create_plan_prompt(plan_data)

        # Get AI response
        ai_response = self.ai_provider.analyze(prompt)

        # Extract duplicates from the report
        all_duplications = []
        for insight in report.top_files:
            if hasattr(insight, "duplications") and insight.duplications:
                all_duplications.extend(insight.duplications)
        duplicates = all_duplications

        # Format as markdown
        return self._format_plan_as_markdown(ai_response, report, duplicates)

    def _create_plan_prompt(self, plan_data: Dict[str, Any]) -> str:
        """Create prompt for AI to generate refactoring plan"""
        prompt = f"""
You are an expert software architect and refactoring specialist. Based on the provided code analysis, 
generate a comprehensive refactoring plan in markdown format with the following structure:

# Refactoring Plan

## Executive Summary
Brief overview of the codebase health and key areas for improvement.

## Phase 1: Critical Issues (High Priority)
Address immediately - security vulnerabilities, critical bugs, major performance issues.

## Phase 2: Code Quality Improvements (Medium Priority)
Improve maintainability, readability, and reduce technical debt.

## Phase 3: Architecture Enhancements (Low Priority)
Long-term architectural improvements and scalability enhancements.

## Detailed Recommendations

### 1. Complexity Reduction
Address functions/classes with high cyclomatic complexity.

### 2. Duplicate Code Elimination
Merge or refactor duplicated code sections.

### 3. Code Smell Resolution
Fix identified code smells like long methods, large classes, etc.

### 4. Unused Code Removal
Remove dead code that is never used.

### 5. Performance Optimizations
Address any performance bottlenecks.

## Implementation Timeline
Suggested timeline for implementing the phases.

## Risk Assessment
Potential risks and mitigation strategies.

## Success Metrics
How to measure the success of the refactoring efforts.

Here is the analysis data:
{json.dumps(plan_data, indent=2)}

Please provide a detailed, actionable refactoring plan following the structure above.
"""
        return prompt

    def _format_plan_as_markdown(
        self, ai_response: str, report: Any, duplicates: List[Any]
    ) -> str:
        """Format the AI response as markdown with additional context"""
        # Add header with metadata
        header = f"""# Refactoring Plan for {report.project_path}

*Generated on: {report.timestamp}*
*Total Files: {report.total_files}*
*Total Lines of Code: {report.total_lines}*
*Languages Detected: {', '.join(report.language_distribution.keys())}*

"""

        # Add analysis summary
        summary = f"""## Analysis Summary

- **Complexity Hotspots**: {len(getattr(report, 'complexity_hotspots', []))} identified
- **Code Duplications**: {len(duplicates)} found
- **Code Smells**: {len(getattr(report, 'recommendations', []))} detected
- **Risk Level**: {self._calculate_risk_level(report)}

"""

        # Combine all sections
        return header + summary + ai_response

    def _calculate_risk_level(self, report: Any) -> str:
        """Calculate overall risk level based on analysis"""
        # Simple risk calculation based on findings
        complexity_count = len(getattr(report, "complexity_hotspots", []))
        smell_count = len(getattr(report, "recommendations", []))

        if complexity_count > 10 or smell_count > 20:
            return "High"
        elif complexity_count > 5 or smell_count > 10:
            return "Medium"
        else:
            return "Low"
