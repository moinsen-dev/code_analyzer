"""
Line counting analyzer
"""

from pathlib import Path
from typing import Tuple

from codeinsight.models.metrics import Language


class LineCounter:
    """Counts lines of code, blank lines, and comment lines in files"""

    def count_lines(self, file_path: Path, language: Language) -> Tuple[int, int, int]:
        """
        Count lines in a file

        Args:
            file_path: Path to the file
            language: Language of the file

        Returns:
            Tuple of (lines_of_code, blank_lines, comment_lines)
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            # If we can't read the file, return zeros
            return (0, 0, 0)

        lines = content.splitlines()
        loc = 0  # lines of code
        blank = 0  # blank lines
        comment = 0  # comment lines

        # Get comment patterns for language
        single_line_comment, multi_line_start, multi_line_end = (
            self._get_comment_patterns(language)
        )

        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            # Check for blank lines
            if not stripped:
                blank += 1
                continue

            # Handle multi-line comments
            if multi_line_start and multi_line_end:
                if not in_multiline_comment and stripped.startswith(multi_line_start):
                    comment += 1
                    in_multiline_comment = not stripped.endswith(
                        multi_line_end
                    ) or stripped.count(multi_line_start) > stripped.count(
                        multi_line_end
                    )
                    continue
                elif in_multiline_comment:
                    comment += 1
                    if stripped.endswith(multi_line_end):
                        in_multiline_comment = False
                    continue

            # Check for single-line comments
            if single_line_comment and stripped.startswith(single_line_comment):
                comment += 1
                continue

            # If we get here, it's a line of code
            loc += 1

        return (loc, blank, comment)

    def _get_comment_patterns(self, language: Language) -> Tuple[str, str, str]:
        """
        Get comment patterns for a language

        Args:
            language: Language to get patterns for

        Returns:
            Tuple of (single_line_comment, multi_line_start, multi_line_end)
        """
        comment_patterns = {
            Language.PYTHON: ("#", '"""', '"""'),
            Language.JAVASCRIPT: ("//", "/*", "*/"),
            Language.TYPESCRIPT: ("//", "/*", "*/"),
            Language.JAVA: ("//", "/*", "*/"),
            Language.CSHARP: ("//", "/*", "*/"),
            Language.CPP: ("//", "/*", "*/"),
            Language.GO: ("//", "/*", "*/"),
            Language.RUST: ("//", "/*", "*/"),
            Language.DART: ("//", "/*", "*/"),
            Language.SWIFT: ("//", "/*", "*/"),
            Language.KOTLIN: ("//", "/*", "*/"),
            Language.PHP: ("//", "/*", "*/"),
            Language.RUBY: ("#", "=begin", "=end"),
            Language.HTML: ("", "<!--", "-->"),
            Language.CSS: ("", "/*", "*/"),
            Language.SQL: ("--", "/*", "*/"),
            Language.YAML: ("#", "", ""),
            Language.JSON: ("", "", ""),  # JSON has no comments
        }

        return comment_patterns.get(language, ("#", "", ""))  # Default to hash comments
