"""Report generation for Code Guardian analysis results."""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template

from .models import AnalysisResults, Issue
from .config import Config


class ReportGenerator:
    """Generates reports in various formats from analysis results."""

    def __init__(self, config: Config):
        """Initialize the report generator."""
        self.config = config

    def generate_json_report(self, results: AnalysisResults, output_path: str) -> None:
        """Generate a JSON report."""
        report_data = {
            'metadata': {
                'tool': 'Code Guardian',
                'version': '0.1.0',
                'generated_at': datetime.datetime.now().isoformat(),
                'execution_time': results.execution_time,
            },
            'summary': {
                'files_scanned': results.files_scanned,
                'security_issues': results.security_issues,
                'performance_issues': results.performance_issues,
                'maintainability_score': results.maintainability_score,
                'ai_generated_percentage': results.ai_generated_percentage,
                'total_issues': len(results.issues),
            },
            'issues': [self._serialize_issue(issue) for issue in results.issues],
            'file_scores': results.file_scores,
            'issues_by_severity': {
                'critical': len([i for i in results.issues if i.severity == 'critical']),
                'high': len([i for i in results.issues if i.severity == 'high']),
                'medium': len([i for i in results.issues if i.severity == 'medium']),
                'low': len([i for i in results.issues if i.severity == 'low']),
            },
            'issues_by_category': {
                'security': len([i for i in results.issues if i.category == 'security']),
                'performance': len([i for i in results.issues if i.category == 'performance']),
                'maintainability': len([i for i in results.issues if i.category == 'maintainability']),
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def generate_html_report(self, results: AnalysisResults, output_path: str) -> None:
        """Generate an HTML report."""
        template = self._get_html_template()

        # Prepare data for template
        template_data = {
            'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results,
            'issues_by_severity': self._group_issues_by_severity(results.issues),
            'issues_by_category': self._group_issues_by_category(results.issues),
            'issues_by_file': self._group_issues_by_file(results.issues),
            'severity_colors': {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#6c757d'
            },
            'category_colors': {
                'security': '#dc3545',
                'performance': '#fd7e14',
                'maintainability': '#17a2b8'
            }
        }

        html_content = template.render(**template_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def generate_sarif_report(self, results: AnalysisResults, output_path: str) -> None:
        """Generate a SARIF (Static Analysis Results Interchange Format) report."""
        sarif_data = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Code Guardian",
                        "version": "0.1.0",
                        "informationUri": "https://github.com/yes-its-shivam/codeGuardian",
                        "rules": self._get_sarif_rules(results.issues)
                    }
                },
                "results": [self._convert_issue_to_sarif(issue) for issue in results.issues]
            }]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sarif_data, f, indent=2)

    def _serialize_issue(self, issue: Issue) -> Dict[str, Any]:
        """Convert an Issue object to a dictionary."""
        return {
            'severity': issue.severity,
            'category': issue.category,
            'message': issue.message,
            'file_path': issue.file_path,
            'line_number': issue.line_number,
            'column': issue.column,
            'rule_id': issue.rule_id,
            'confidence': issue.confidence,
            'source_snippet': issue.source_snippet,
            'suggestion': issue.suggestion
        }

    def _group_issues_by_severity(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """Group issues by severity level."""
        groups = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for issue in issues:
            if issue.severity in groups:
                groups[issue.severity].append(issue)
        return groups

    def _group_issues_by_category(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """Group issues by category."""
        groups = {}
        for issue in issues:
            if issue.category not in groups:
                groups[issue.category] = []
            groups[issue.category].append(issue)
        return groups

    def _group_issues_by_file(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """Group issues by file path."""
        groups = {}
        for issue in issues:
            if issue.file_path not in groups:
                groups[issue.file_path] = []
            groups[issue.file_path].append(issue)
        return groups

    def _get_html_template(self) -> Template:
        """Get the HTML report template."""
        template_str = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Guardian Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .title { font-size: 2.5rem; color: #2c3e50; margin: 0; }
        .subtitle { color: #6c757d; margin: 10px 0 0 0; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
        .metric-value { font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
        .metric-label { color: #6c757d; font-size: 0.9rem; }
        .section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .section-title { font-size: 1.5rem; margin-bottom: 20px; color: #2c3e50; }
        .issue { padding: 15px; border-left: 4px solid; margin-bottom: 10px; background: #f8f9fa; border-radius: 0 4px 4px 0; }
        .issue-critical { border-left-color: #dc3545; }
        .issue-high { border-left-color: #fd7e14; }
        .issue-medium { border-left-color: #ffc107; }
        .issue-low { border-left-color: #6c757d; }
        .issue-header { font-weight: bold; margin-bottom: 5px; }
        .issue-meta { font-size: 0.9rem; color: #6c757d; margin-bottom: 10px; }
        .issue-suggestion { background: #e3f2fd; padding: 10px; border-radius: 4px; font-size: 0.9rem; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; }
        .badge-critical { background: #dc3545; color: white; }
        .badge-high { background: #fd7e14; color: white; }
        .badge-medium { background: #ffc107; color: #212529; }
        .badge-low { background: #6c757d; color: white; }
        .score-good { color: #28a745; }
        .score-warning { color: #ffc107; }
        .score-danger { color: #dc3545; }
        code { background: #f1f3f4; padding: 2px 4px; border-radius: 3px; font-family: 'Monaco', 'Consolas', monospace; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🛡️ Code Guardian Report</h1>
            <p class="subtitle">Generated on {{ generated_at }}</p>
        </div>

        <div class="summary-grid">
            <div class="metric-card">
                <div class="metric-value">{{ results.files_scanned }}</div>
                <div class="metric-label">Files Scanned</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ results.security_issues }}</div>
                <div class="metric-label">Security Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ results.performance_issues }}</div>
                <div class="metric-label">Performance Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {% if results.maintainability_score >= 7 %}score-good{% elif results.maintainability_score >= 5 %}score-warning{% else %}score-danger{% endif %}">
                    {{ "%.1f"|format(results.maintainability_score) }}/10
                </div>
                <div class="metric-label">Maintainability Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ "%.1f"|format(results.ai_generated_percentage) }}%</div>
                <div class="metric-label">AI Generated Code</div>
            </div>
        </div>

        {% if results.issues %}
        <div class="section">
            <h2 class="section-title">📋 Issues Found</h2>
            {% for issue in results.issues[:20] %}
            <div class="issue issue-{{ issue.severity }}">
                <div class="issue-header">
                    <span class="badge badge-{{ issue.severity }}">{{ issue.severity }}</span>
                    {{ issue.message }}
                </div>
                <div class="issue-meta">
                    📁 <code>{{ issue.file_path }}</code> at line {{ issue.line_number }}
                    {% if issue.rule_id %} • Rule: {{ issue.rule_id }}{% endif %}
                </div>
                {% if issue.source_snippet %}
                <div style="margin: 10px 0;"><code>{{ issue.source_snippet }}</code></div>
                {% endif %}
                {% if issue.suggestion %}
                <div class="issue-suggestion">
                    💡 <strong>Suggestion:</strong> {{ issue.suggestion }}
                </div>
                {% endif %}
            </div>
            {% endfor %}
            {% if results.issues|length > 20 %}
            <p><em>... and {{ results.issues|length - 20 }} more issues. See JSON report for complete details.</em></p>
            {% endif %}
        </div>
        {% endif %}

        <div class="section">
            <h2 class="section-title">📊 Analysis Summary</h2>
            <p>Scanned <strong>{{ results.files_scanned }}</strong> files in <strong>{{ "%.2f"|format(results.execution_time) }}</strong> seconds.</p>
            {% if results.ai_generated_percentage > 50 %}
            <p>⚠️ This codebase appears to contain a significant amount of AI-generated code ({{ "%.1f"|format(results.ai_generated_percentage) }}%). Consider reviewing AI-generated sections carefully.</p>
            {% endif %}
            {% if results.has_critical_issues() %}
            <p>🚨 <strong>Critical issues found!</strong> Please address these security vulnerabilities immediately.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>'''
        return Template(template_str)

    def _get_sarif_rules(self, issues: List[Issue]) -> List[Dict[str, Any]]:
        """Generate SARIF rules from issues."""
        rules = {}
        for issue in issues:
            if issue.rule_id and issue.rule_id not in rules:
                rules[issue.rule_id] = {
                    "id": issue.rule_id,
                    "name": issue.rule_id.replace('.', '_').upper(),
                    "shortDescription": {"text": issue.message},
                    "fullDescription": {"text": issue.suggestion or issue.message},
                    "defaultConfiguration": {
                        "level": self._severity_to_sarif_level(issue.severity)
                    }
                }
        return list(rules.values())

    def _convert_issue_to_sarif(self, issue: Issue) -> Dict[str, Any]:
        """Convert an Issue to SARIF format."""
        return {
            "ruleId": issue.rule_id,
            "level": self._severity_to_sarif_level(issue.severity),
            "message": {"text": issue.message},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": issue.file_path},
                    "region": {
                        "startLine": issue.line_number,
                        "startColumn": issue.column or 1
                    }
                }
            }]
        }

    def _severity_to_sarif_level(self, severity: str) -> str:
        """Convert severity to SARIF level."""
        mapping = {
            'critical': 'error',
            'high': 'error',
            'medium': 'warning',
            'low': 'note'
        }
        return mapping.get(severity, 'warning')