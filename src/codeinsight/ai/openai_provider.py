"""
OpenAI provider implementation for Refactoroscope
"""

import os
import time
from typing import Any, Optional

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from codeinsight.ai.base import (
    AIAnalysisResult,
    AIProvider,
    AIProviderType,
    CodeContext,
)
from codeinsight.ai.factory import AIProviderFactory


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-5-mini", **kwargs: Any
    ) -> None:
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is not installed. Install it with 'pip install openai'"
            )

        self.model = model
        self.client = None

        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        """Check if OpenAI is properly configured and available"""
        return self.client is not None and self.api_key is not None

    def analyze(self, prompt: str) -> str:
        """
        Analyze a prompt and return the AI's response as a string.

        Args:
            prompt: The prompt to analyze

        Returns:
            The AI's response as a string
        """
        if not self.is_available():
            raise RuntimeError("OpenAI provider is not properly configured")

        try:
            # Call OpenAI API
            if self.client is not None:
                # Determine which parameter to use based on model name
                # Newer models (gpt-5-mini, etc.) use max_completion_tokens
                # Older models (gpt-3.5-turbo, etc.) use max_tokens
                # Newer models may not support temperature=0.1, so we use 1.0 for them
                temperature = self._get_appropriate_temperature()
                if "gpt-5" in self.model or "gpt-4o" in self.model:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert software architect and refactoring specialist.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=temperature,
                        max_completion_tokens=4000,  # Increased token limit for refactoring plans
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert software architect and refactoring specialist.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=temperature,
                        max_tokens=4000,  # Increased token limit for refactoring plans
                    )

            # Process response
            response_content = (
                response.choices[0].message.content
                if response.choices[0].message.content
                else ""
            )

            return response_content

        except Exception as e:
            raise RuntimeError(f"Error analyzing prompt with OpenAI: {str(e)}")

    def analyze_code_quality(self, context: CodeContext) -> AIAnalysisResult:
        """Analyze code quality using OpenAI"""
        if not self.is_available():
            raise RuntimeError("OpenAI provider is not properly configured")

        start_time = time.time()

        # Prepare the prompt
        prompt = self._create_analysis_prompt(context)

        try:
            # Call OpenAI API
            if self.client is not None:
                # Get appropriate temperature based on model
                temperature = self._get_appropriate_temperature()

                # Determine which parameter to use based on model name
                # Newer models (gpt-5-mini, etc.) use max_completion_tokens
                # Older models (gpt-3.5-turbo, etc.) use max_tokens
                if "gpt-5" in self.model or "gpt-4o" in self.model:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert code reviewer providing actionable suggestions for code quality improvements.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=temperature,
                        max_completion_tokens=2000,
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert code reviewer providing actionable suggestions for code quality improvements.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=temperature,
                        max_tokens=2000,
                    )

            # Process response
            response_content = (
                response.choices[0].message.content
                if response.choices[0].message.content
                else ""
            )
            suggestions = self._parse_response(response_content)

            execution_time = time.time() - start_time

            # Get token usage if available
            tokens_used = None
            cost = None
            if hasattr(response, "usage") and response.usage is not None:
                tokens_used = response.usage.total_tokens
                # Rough cost calculation (prices vary by model)
                if "gpt-4" in self.model:
                    cost = tokens_used * 0.00003  # Approximate cost for GPT-4
                else:
                    cost = tokens_used * 0.000002  # Approximate cost for GPT-3.5

            return AIAnalysisResult(
                provider=self.provider_name,
                file_path=context.file_path,
                suggestions=suggestions,
                confidence=0.9,  # High confidence for OpenAI
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Error analyzing code with OpenAI: {str(e)}")

    def _create_analysis_prompt(self, context: CodeContext) -> str:
        """Create a prompt for code analysis"""
        prompt = f"""
Analyze the following {context.language} code and provide quality suggestions:

File: {context.file_path}

{context.file_content}

Please provide specific, actionable suggestions in the following format:
1. [ISSUE_TYPE] [LINE_NUMBERS]: [DESCRIPTION]
   Suggestion: [IMPROVEMENT_SUGGESTION]

Focus on:
- Code readability and maintainability
- Performance optimizations
- Potential bugs or edge cases
- Best practices for {context.language}
- Security vulnerabilities

Keep suggestions concise but detailed enough to be actionable.
"""
        return prompt

    def _parse_response(self, response_text: str) -> list:
        """Parse the AI response into structured suggestions"""
        # Simple parsing - in a real implementation, this would be more sophisticated
        suggestions = []
        lines = response_text.strip().split("\n")

        current_suggestion: dict = {}
        for line in lines:
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                # Parse the numbered suggestion
                parts = line.split(":", 1)
                if len(parts) == 2:
                    current_suggestion = {
                        "description": parts[1].strip(),
                        "line_numbers": None,
                        "type": "general",
                    }
            elif line.strip().startswith("Suggestion:"):
                if current_suggestion:
                    current_suggestion["suggestion"] = line.replace(
                        "Suggestion:", ""
                    ).strip()

        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions

    def _get_appropriate_temperature(self) -> float:
        """Get appropriate temperature value based on model capabilities"""
        # Models that don't support temperature=0.1 should use 1.0
        models_requiring_higher_temp = [
            "gpt-5",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4-1106",
            "gpt-4-0125",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-1106",
        ]

        for model_prefix in models_requiring_higher_temp:
            if model_prefix in self.model:
                return 1.0

        # Default to 0.1 for other models
        return 0.1

    @property
    def provider_name(self) -> str:
        return AIProviderType.OPENAI.value


# Register the provider
AIProviderFactory.register_provider(AIProviderType.OPENAI, OpenAIProvider)
