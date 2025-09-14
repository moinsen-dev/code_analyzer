"""
Domain models for code analysis
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class Language(str, Enum):
    """Supported programming languages"""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    DART = "dart"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    PHP = "php"
    RUBY = "ruby"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"
    # Add more as needed


@dataclass
class HalsteadMetrics:
    """Halstead complexity metrics"""

    program_length: int = 0
    vocabulary_size: int = 0
    volume: float = 0.0
    difficulty: float = 0.0
    effort: float = 0.0


@dataclass
class Duplication:
    """Code duplication information"""

    type: str  # function, class, block, etc.
    name: str  # Name of the duplicated element
    line: int  # Line number where duplication starts
    count: int  # Number of duplicates found
    clone_type: str = "exact"  # exact, renamed, modified, semantic
    similarity: float = 1.0  # Similarity score (0.0 to 1.0)
    locations: List[Dict[str, Any]] = field(default_factory=list)  # Detailed locations


@dataclass
class FileMetrics:
    """Metrics for a single file"""

    path: Path
    relative_path: str
    language: Language
    lines_of_code: int
    blank_lines: int
    comment_lines: int
    size_bytes: int
    last_modified: datetime


@dataclass
class ComplexityMetrics:
    """Code complexity metrics"""

    cyclomatic_complexity: float
    cognitive_complexity: float
    maintainability_index: float
    technical_debt_ratio: float
    halstead_metrics: HalsteadMetrics = field(default_factory=HalsteadMetrics)


@dataclass
class UnusedCodeFinding:
    """Represents a single unused code finding"""

    type: str  # function, class, variable, import, etc.
    name: str  # Name of the unused element
    line: int  # Line number where it's defined
    confidence: float  # Confidence level (0.0 to 1.0)
    reason: str  # Explanation of why it's considered unused


@dataclass
class UnusedFileFinding:
    """Represents a completely unused file"""

    path: Path
    confidence: float
    reason: str


@dataclass
class CodeInsights:
    """Insights for a single code file"""

    file_metrics: FileMetrics
    complexity_metrics: Optional[ComplexityMetrics] = None
    code_smells: List[str] = field(default_factory=list)
    duplications: List[Duplication] = field(default_factory=list)
    unused_code: List[UnusedCodeFinding] = field(default_factory=list)


@dataclass
class AnalysisReport:
    """Complete analysis report"""

    project_path: Path
    timestamp: datetime
    total_files: int
    total_lines: int
    total_size: int
    language_distribution: Dict[Language, int]
    top_files: List[CodeInsights]
    recommendations: List[str] = field(default_factory=list)

    def json(self) -> str:
        """Convert report to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization"""
        from dataclasses import asdict
        from datetime import datetime

        def json_serializer(obj: Any) -> Any:
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Language):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        result: Dict[str, Any] = json.loads(
            json.dumps(asdict(self), default=json_serializer)
        )
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisReport":
        """Create AnalysisReport from dictionary"""
        from datetime import datetime

        # Convert timestamp
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        # Convert project_path
        data["project_path"] = Path(data["project_path"])

        # Convert language_distribution keys
        lang_dist = {}
        for lang_key, count in data["language_distribution"].items():
            lang_dist[Language(lang_key)] = count
        data["language_distribution"] = lang_dist

        # Convert top_files
        top_files = []
        for file_data in data["top_files"]:
            # Convert file_metrics
            file_metrics_data = file_data["file_metrics"]
            file_metrics_data["path"] = Path(file_metrics_data["path"])
            file_metrics_data["language"] = Language(file_metrics_data["language"])
            file_metrics_data["last_modified"] = datetime.fromisoformat(
                file_metrics_data["last_modified"]
            )
            file_metrics = FileMetrics(**file_metrics_data)

            # Convert complexity_metrics if present
            complexity_metrics = None
            if file_data["complexity_metrics"]:
                # Convert halstead_metrics if present
                halstead_data = file_data["complexity_metrics"].get("halstead_metrics")
                if halstead_data:
                    halstead_metrics = HalsteadMetrics(**halstead_data)
                    file_data["complexity_metrics"][
                        "halstead_metrics"
                    ] = halstead_metrics
                complexity_metrics = ComplexityMetrics(
                    **file_data["complexity_metrics"]
                )

            # Create CodeInsights
            code_insights = CodeInsights(
                file_metrics=file_metrics,
                complexity_metrics=complexity_metrics,
                code_smells=file_data.get("code_smells", []),
                duplications=file_data.get("duplications", []),
            )
            top_files.append(code_insights)

        data["top_files"] = top_files

        return cls(**data)
