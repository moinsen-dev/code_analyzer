"""
Anthropic provider implementation for Refactoroscope
"""

import os
import time
from typing import Any, Optional

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from codeinsight.ai.base import (
    AIAnalysisResult,
    AIProvider,
    AIProviderType,
    CodeContext,
)
from codeinsight.ai.factory import AIProviderFactory


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        **kwargs: Any,
    ) -> None:
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package is not installed. Install it with 'pip install anthropic'"
            )

        self.model = model
        self.client = None

        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def is_available(self) -> bool:
        """Check if Anthropic is properly configured and available"""
        return self.client is not None and self.api_key is not None

    def analyze_code_quality(self, context: CodeContext) -> AIAnalysisResult:
        """Analyze code quality using Anthropic"""
        if not self.is_available():
            raise RuntimeError("Anthropic provider is not properly configured")

        start_time = time.time()

        # Prepare the prompt
        prompt = self._create_analysis_prompt(context)

        try:
            # Call Anthropic API
            if self.client is not None:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )

            # Process response
            response_text = ""
            if (
                response.content
                and len(response.content) > 0
                and hasattr(response.content[0], "text")
            ):
                response_text = response.content[0].text
            suggestions = self._parse_response(response_text)

            execution_time = time.time() - start_time

            # Get token usage if available
            tokens_used = None
            cost = None
            if hasattr(response, "usage"):
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                # Rough cost calculation (prices vary by model)
                if "claude-3-opus" in self.model:
                    cost = tokens_used * 0.000015  # Approximate cost for Claude 3 Opus
                elif "claude-3-sonnet" in self.model:
                    cost = (
                        tokens_used * 0.000003
                    )  # Approximate cost for Claude 3 Sonnet
                else:
                    cost = (
                        tokens_used * 0.00000025
                    )  # Approximate cost for Claude 3 Haiku

            return AIAnalysisResult(
                provider=self.provider_name,
                file_path=context.file_path,
                suggestions=suggestions,
                confidence=0.85,  # High confidence for Anthropic
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Error analyzing code with Anthropic: {str(e)}")

    def _create_analysis_prompt(self, context: CodeContext) -> str:
        """Create a prompt for code analysis"""
        prompt = f"""
Human: Analyze the following {context.language} code and provide quality suggestions:

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

Assistant:
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

    def analyze(self, prompt: str) -> str:
        """
        Analyze a prompt and return the AI's response as a string.

        Args:
            prompt: The prompt to analyze

        Returns:
            The AI's response as a string
        """
        if not self.is_available():
            raise RuntimeError("Anthropic provider is not available")

        try:
            # Call Anthropic API
            if self.client is not None:
                # For general analysis, we'll use a simpler approach
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,  # Increased token limit for detailed responses
                    temperature=0.1,  # Low temperature for more deterministic responses
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )
                # Handle different content types properly
                if message.content and len(message.content) > 0:
                    content_block = message.content[0]
                    if hasattr(content_block, "text"):
                        return content_block.text
                    else:
                        # For other content types, convert to string
                        return str(content_block)
                else:
                    return ""
            else:
                raise RuntimeError("Anthropic client is not initialized")
        except Exception as e:
            raise RuntimeError(f"Error analyzing with Anthropic: {e}")

    @property
    def provider_name(self) -> str:
        return AIProviderType.ANTHROPIC.value


# Register the provider
AIProviderFactory.register_provider(AIProviderType.ANTHROPIC, AnthropicProvider)
