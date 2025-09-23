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

    def generate_plan(self, path: Path, verbose: bool = False) -> str:
        """
        Generate a refactoring plan for the given path

        Args:
            path: Path to analyze
            verbose: Whether to show verbose output

        Returns:
            Markdown formatted refactoring plan
        """
        # Run initial analysis without AI to avoid analyzing individual files
        if verbose:
            print("   → Collecting code metrics...")
        scanner = Scanner(path, enable_duplicates=True, enable_ai=False)
        report = scanner.analyze(path, include_complexity=True)
        if verbose:
            print("   → Code analysis complete")

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

        if verbose:
            print("   → Sending analysis data to AI for plan generation...")
        # Create prompt for AI
        prompt = self._create_plan_prompt(plan_data)

        if verbose:
            print("   → AI Prompt:")
            print("   ------------------------")
            print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
            print("   ------------------------")

        # Get AI response
        try:
            ai_response = self.ai_provider.analyze(prompt)
            if verbose:
                print("   → AI Response:")
                print("   ------------------------")
                print(
                    ai_response[:1000] + "..."
                    if len(ai_response) > 1000
                    else ai_response
                )
                print("   ------------------------")

            if not ai_response or ai_response.strip() == "":
                ai_response = "# Refactoring Plan\n\nUnable to generate a detailed plan. Please try again or check your AI provider configuration."
        except Exception as e:
            if verbose:
                print(f"   → AI Error: {e}")
            ai_response = f"# Refactoring Plan\n\nError generating plan: {str(e)}\n\nPlease check your AI provider configuration and try again."
        if verbose:
            print("   → AI plan generation complete")

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

        # Send the exact analysis data as JSON to the AI without any filtering
        prompt = f"""You are an expert software architect and refactoring specialist. Based on the following code analysis JSON data, generate a comprehensive refactoring plan.

## Code Analysis Data
{json.dumps(plan_data, indent=2)}

## Instructions
Analyze the above JSON code analysis data and generate a detailed refactoring plan with the following structure:

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

Provide specific, actionable recommendations with concrete examples from the analysis data. Reference specific files, line numbers, and metrics where applicable. Be concise but thorough. Use markdown format."""

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
