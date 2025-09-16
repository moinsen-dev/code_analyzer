"""
Ollama provider implementation for Refactoroscope
"""

import time
from typing import Any, Optional

import requests

from codeinsight.ai.base import (
    AIAnalysisResult,
    AIProvider,
    AIProviderType,
    CodeContext,
)
from codeinsight.ai.factory import AIProviderFactory


class OllamaProvider(AIProvider):
    """Ollama provider implementation"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "qwen3-coder",
        base_url: str = "http://localhost:11434",
        **kwargs: Any,
    ) -> None:
        self.model = model
        self.base_url = base_url
        self.api_key = api_key  # Ollama typically doesn't require API keys

    def is_available(self) -> bool:
        """Check if Ollama is properly configured and available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def analyze_code_quality(self, context: CodeContext) -> AIAnalysisResult:
        """Analyze code quality using Ollama"""
        if not self.is_available():
            raise RuntimeError("Ollama is not available. Make sure Ollama is running.")

        start_time = time.time()

        # Prepare the prompt
        prompt = self._create_analysis_prompt(context)

        try:
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 1000},
                },
                timeout=120,  # Longer timeout for local models
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API returned status {response.status_code}")

            response_data = response.json()
            response_text = response_data.get("response", "")

            # Process response
            suggestions = self._parse_response(response_text)

            execution_time = time.time() - start_time

            # Get token usage if available
            tokens_used = response_data.get("eval_count", 0)
            cost = 0.0  # Ollama is free for local models

            return AIAnalysisResult(
                provider=self.provider_name,
                file_path=context.file_path,
                suggestions=suggestions,
                confidence=0.7,  # Moderate confidence for local models
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Error analyzing code with Ollama: {str(e)}")

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
            raise RuntimeError("Ollama provider is not available")

        try:
            # Call Ollama API using requests
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "options": {
                        "temperature": 0.1,  # Low temperature for more deterministic responses
                    },
                    "stream": False,
                },
                timeout=300,  # 5 minute timeout for complex analyses
            )

            if response.status_code == 200:
                response_data = response.json()
                return response_data["message"]["content"]
            else:
                raise RuntimeError(
                    f"Ollama API returned status code {response.status_code}"
                )
        except Exception as e:
            raise RuntimeError(f"Error analyzing with Ollama: {e}")

    @property
    def provider_name(self) -> str:
        return AIProviderType.OLLAMA.value


# Register the provider
AIProviderFactory.register_provider(AIProviderType.OLLAMA, OllamaProvider)
