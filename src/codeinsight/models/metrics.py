"""
Domain models for code analysis
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from enum import Enum

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

@dataclass
class CodeInsights:
    """Insights for a single code file"""
    file_metrics: FileMetrics
    complexity_metrics: Optional[ComplexityMetrics] = None
    code_smells: List[str] = None
    duplications: List[Any] = None
    
    def __post_init__(self):
        if self.code_smells is None:
            self.code_smells = []
        if self.duplications is None:
            self.duplications = []

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
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
    
    def json(self) -> str:
        """Convert report to JSON string"""
        import json
        from dataclasses import asdict
        from datetime import datetime
        
        def json_serializer(obj):
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Language):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(asdict(self), default=json_serializer, indent=2)