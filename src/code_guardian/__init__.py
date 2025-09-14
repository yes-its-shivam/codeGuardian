"""
Code Guardian - AI-generated code quality analyzer and security scanner.

A comprehensive tool for analyzing AI-generated code for security vulnerabilities,
performance issues, and maintainability problems.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .analyzer import CodeAnalyzer
from .scanner import SecurityScanner
from .performance import PerformanceAnalyzer
from .maintainability import MaintainabilityScorer
from .report import ReportGenerator
from .models import Issue, AnalysisResults

__all__ = [
    "CodeAnalyzer",
    "SecurityScanner",
    "PerformanceAnalyzer",
    "MaintainabilityScorer",
    "ReportGenerator",
    "Issue",
    "AnalysisResults",
]