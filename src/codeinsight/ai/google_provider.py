"""
Google Gemini provider implementation for Refactoroscope
"""

import os
import time
from typing import Any, Optional

try:
    import google.generativeai as genai

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from codeinsight.ai.base import (
    AIAnalysisResult,
    AIProvider,
    AIProviderType,
    CodeContext,
)
from codeinsight.ai.factory import AIProviderFactory


class GoogleProvider(AIProvider):
    """Google Gemini provider implementation"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        **kwargs: Any,
    ) -> None:
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "google-generativeai package is not installed. Install it with 'pip install google-generativeai'"
            )

        self.model = model
        self.client = None

        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(model)

    def is_available(self) -> bool:
        """Check if Google Gemini is properly configured and available"""
        return self.client is not None and self.api_key is not None

    def analyze_code_quality(self, context: CodeContext) -> AIAnalysisResult:
        """Analyze code quality using Google Gemini"""
        if not self.is_available():
            raise RuntimeError("Google Gemini provider is not properly configured")

        start_time = time.time()

        # Prepare the prompt
        prompt = self._create_analysis_prompt(context)

        try:
            # Call Google Gemini API
            if self.client is not None:
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1, max_output_tokens=1000
                    ),
                )

            # Process response
            suggestions = self._parse_response(response.text)

            execution_time = time.time() - start_time

            # Get token usage if available
            tokens_used = None
            cost = None
            if hasattr(response, "usage_metadata"):
                tokens_used = response.usage_metadata.total_token_count
                # Rough cost calculation (prices vary by model)
                cost = tokens_used * 0.0000005  # Approximate cost for Gemini Pro

            return AIAnalysisResult(
                provider=self.provider_name,
                file_path=context.file_path,
                suggestions=suggestions,
                confidence=0.8,  # Good confidence for Gemini
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Error analyzing code with Google Gemini: {str(e)}")

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

    def analyze(self, prompt: str) -> str:
        """
        Analyze a prompt and return the AI's response as a string.

        Args:
            prompt: The prompt to analyze

        Returns:
            The AI's response as a string
        """
        if not self.is_available():
            raise RuntimeError("Google provider is not available")

        try:
            # Call Google API
            if self.client is not None:
                # For general analysis, we'll use a simpler approach
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": 4000,  # Increased token limit for detailed responses
                        "temperature": 0.1,  # Low temperature for more deterministic responses
                    },
                )
                return response.text
            else:
                raise RuntimeError("Google client is not initialized")
        except Exception as e:
            raise RuntimeError(f"Error analyzing with Google: {e}")

    @property
    def provider_name(self) -> str:
        return AIProviderType.GOOGLE.value


# Register the provider
AIProviderFactory.register_provider(AIProviderType.GOOGLE, GoogleProvider)
