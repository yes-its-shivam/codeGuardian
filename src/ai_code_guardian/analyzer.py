"""Main analyzer orchestrator for Code Guardian."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import fnmatch

from .config import Config
from .models import Issue, AnalysisResults


class CodeAnalyzer:
    """Main analyzer that orchestrates all analysis components."""

    def __init__(self, config: Config):
        """Initialize the analyzer with configuration."""
        self.config = config

        # Initialize analyzers based on configuration (import here to avoid circular imports)
        from .scanner import SecurityScanner
        from .performance import PerformanceAnalyzer
        from .maintainability import MaintainabilityScorer
        from .ai_detector import AIPatternDetector

        self.security_scanner = SecurityScanner(config) if config.security_enabled else None
        self.performance_analyzer = PerformanceAnalyzer(config) if config.performance_enabled else None
        self.maintainability_scorer = MaintainabilityScorer(config) if config.maintainability_enabled else None
        self.ai_detector = AIPatternDetector(config) if config.ai_detection_enabled else None

    def analyze_paths(self, paths: List[str], exclude_patterns: List[str] = None,
                     min_severity: str = 'medium', detect_ai_patterns: bool = True) -> AnalysisResults:
        """Analyze multiple paths (files or directories)."""
        import time
        start_time = time.time()

        exclude_patterns = exclude_patterns or []
        exclude_patterns.extend(self.config.exclude_patterns)

        # Collect all files to analyze
        files_to_analyze = []
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                if self._should_analyze_file(path, exclude_patterns):
                    files_to_analyze.append(path)
            elif path.is_dir():
                files_to_analyze.extend(self._collect_files_from_directory(path, exclude_patterns))

        # Analyze files
        results = AnalysisResults()
        results.files_scanned = len(files_to_analyze)

        all_issues = []
        ai_scores = []

        for file_path in files_to_analyze:
            file_issues, file_scores = self._analyze_file(file_path, detect_ai_patterns)
            all_issues.extend(file_issues)
            results.file_scores[str(file_path)] = file_scores

            # Collect AI detection scores
            if 'ai_confidence' in file_scores:
                ai_scores.append(file_scores['ai_confidence'])

        # Filter issues by minimum severity
        severity_levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        min_level = severity_levels.get(min_severity, 1)

        results.issues = [
            issue for issue in all_issues
            if severity_levels.get(issue.severity, 0) >= min_level
        ]

        # Calculate summary statistics
        results.security_issues = len([i for i in results.issues if i.category == 'security'])
        results.performance_issues = len([i for i in results.issues if i.category == 'performance'])

        # Calculate overall maintainability score
        maintainability_scores = [
            scores.get('maintainability_score', 10.0)
            for scores in results.file_scores.values()
        ]
        if maintainability_scores:
            results.maintainability_score = sum(maintainability_scores) / len(maintainability_scores)

        # Calculate AI-generated percentage
        if ai_scores:
            results.ai_generated_percentage = sum(ai_scores) / len(ai_scores) * 100

        results.execution_time = time.time() - start_time
        return results

    def _analyze_file(self, file_path: Path, detect_ai_patterns: bool = True) -> tuple:
        """Analyze a single file and return issues and scores."""
        issues = []
        scores = {}

        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Security analysis
            if self.security_scanner:
                security_issues = self.security_scanner.scan_file(str(file_path), content)
                issues.extend(security_issues)

            # Performance analysis
            if self.performance_analyzer:
                perf_issues, perf_score = self.performance_analyzer.analyze_file(str(file_path), content)
                issues.extend(perf_issues)
                scores['performance_score'] = perf_score

            # Maintainability analysis
            if self.maintainability_scorer:
                maint_issues, maint_score = self.maintainability_scorer.score_file(str(file_path), content)
                issues.extend(maint_issues)
                scores['maintainability_score'] = maint_score

            # AI pattern detection
            if detect_ai_patterns and self.ai_detector:
                ai_confidence, ai_patterns = self.ai_detector.detect_ai_patterns(content, str(file_path))
                scores['ai_confidence'] = ai_confidence
                scores['ai_patterns'] = ai_patterns

        except Exception as e:
            # Add error as an issue
            issues.append(Issue(
                severity='medium',
                category='analysis',
                message=f'Failed to analyze file: {str(e)}',
                file_path=str(file_path),
                line_number=0
            ))

        return issues, scores

    def _collect_files_from_directory(self, directory: Path, exclude_patterns: List[str]) -> List[Path]:
        """Recursively collect files from directory."""
        files = []
        supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.php'}

        for path in directory.rglob('*'):
            if path.is_file() and path.suffix in supported_extensions:
                if self._should_analyze_file(path, exclude_patterns):
                    files.append(path)

        return files

    def _should_analyze_file(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be analyzed based on exclude patterns."""
        path_str = str(file_path)

        for pattern in exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return False

        return True