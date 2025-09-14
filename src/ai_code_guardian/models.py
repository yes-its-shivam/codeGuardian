"""Data models for Code Guardian."""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class Issue:
    """Represents a code quality issue."""
    severity: str
    category: str
    message: str
    file_path: str
    line_number: int
    column: int = 0
    rule_id: str = ""
    confidence: float = 1.0
    source_snippet: str = ""
    suggestion: str = ""


@dataclass
class AnalysisResults:
    """Container for analysis results."""
    files_scanned: int = 0
    security_issues: int = 0
    performance_issues: int = 0
    maintainability_score: float = 10.0
    ai_generated_percentage: float = 0.0
    issues: List[Issue] = field(default_factory=list)
    file_scores: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    execution_time: float = 0.0

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return any(issue.severity == 'critical' for issue in self.issues)

    def get_issues_by_severity(self, severity: str) -> List[Issue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: str) -> List[Issue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]