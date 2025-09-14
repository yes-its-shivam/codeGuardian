"""Tests for the main code analyzer."""

import pytest
from pathlib import Path
from code_guardian.analyzer import CodeAnalyzer
from code_guardian.models import Issue, AnalysisResults
from code_guardian.config import Config


def test_analyzer_initialization():
    """Test analyzer initialization with config."""
    config = Config()
    analyzer = CodeAnalyzer(config)

    assert analyzer.config is config
    assert analyzer.security_scanner is not None
    assert analyzer.performance_analyzer is not None
    assert analyzer.maintainability_scorer is not None
    assert analyzer.ai_detector is not None


def test_analyzer_with_disabled_components():
    """Test analyzer with disabled components."""
    config_dict = {
        'security': {'enabled': False},
        'performance': {'enabled': False},
        'maintainability': {'enabled': False},
        'ai_detection': {'enabled': False}
    }
    config = Config(config_dict)
    analyzer = CodeAnalyzer(config)

    assert analyzer.security_scanner is None
    assert analyzer.performance_analyzer is None
    assert analyzer.maintainability_scorer is None
    assert analyzer.ai_detector is None


def test_should_analyze_file():
    """Test file filtering logic."""
    config = Config()
    analyzer = CodeAnalyzer(config)

    # Should analyze Python files
    assert analyzer._should_analyze_file(Path('test.py'), [])

    # Should not analyze excluded files
    assert not analyzer._should_analyze_file(Path('test.pyc'), ['*.pyc'])
    assert not analyzer._should_analyze_file(Path('__pycache__/test.py'), ['__pycache__/'])


def test_analyze_simple_python_code():
    """Test analyzing simple Python code."""
    config = Config()
    analyzer = CodeAnalyzer(config)

    # Create a temporary Python file content
    python_code = '''
def hello_world():
    """A simple function."""
    print("Hello, World!")
    return "success"

if __name__ == "__main__":
    hello_world()
'''

    # Mock file analysis (in real scenario, this would be a file)
    issues, scores = analyzer._analyze_file(Path('test.py'), detect_ai_patterns=True)

    # Should return some form of results
    assert isinstance(issues, list)
    assert isinstance(scores, dict)


def test_analysis_results_creation():
    """Test AnalysisResults dataclass."""
    results = AnalysisResults()

    assert results.files_scanned == 0
    assert results.security_issues == 0
    assert results.performance_issues == 0
    assert results.maintainability_score == 10.0
    assert results.ai_generated_percentage == 0.0
    assert results.issues == []
    assert not results.has_critical_issues()


def test_analysis_results_with_critical_issue():
    """Test AnalysisResults with critical issues."""
    issue = Issue(
        severity='critical',
        category='security',
        message='Test critical issue',
        file_path='test.py',
        line_number=1
    )

    results = AnalysisResults(issues=[issue])
    assert results.has_critical_issues()


def test_get_issues_by_severity():
    """Test filtering issues by severity."""
    issues = [
        Issue('critical', 'security', 'Critical issue', 'test.py', 1),
        Issue('high', 'performance', 'High issue', 'test.py', 2),
        Issue('medium', 'maintainability', 'Medium issue', 'test.py', 3),
        Issue('low', 'maintainability', 'Low issue', 'test.py', 4),
    ]

    results = AnalysisResults(issues=issues)

    assert len(results.get_issues_by_severity('critical')) == 1
    assert len(results.get_issues_by_severity('high')) == 1
    assert len(results.get_issues_by_severity('medium')) == 1
    assert len(results.get_issues_by_severity('low')) == 1


def test_get_issues_by_category():
    """Test filtering issues by category."""
    issues = [
        Issue('high', 'security', 'Security issue', 'test.py', 1),
        Issue('medium', 'performance', 'Performance issue', 'test.py', 2),
        Issue('low', 'maintainability', 'Maintainability issue', 'test.py', 3),
    ]

    results = AnalysisResults(issues=issues)

    assert len(results.get_issues_by_category('security')) == 1
    assert len(results.get_issues_by_category('performance')) == 1
    assert len(results.get_issues_by_category('maintainability')) == 1