"""Security vulnerability scanner for AI-generated code."""

import re
import ast
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Issue
from .config import Config


class SecurityScanner:
    """Scans code for security vulnerabilities commonly found in AI-generated code."""

    def __init__(self, config: Config):
        """Initialize the security scanner."""
        self.config = config
        self._init_vulnerability_patterns()

    def _init_vulnerability_patterns(self):
        """Initialize vulnerability detection patterns."""
        # SQL Injection patterns
        self.sql_injection_patterns = [
            (r'execute\s*\(\s*["\'].*%.*["\']', 'SQL injection via string formatting'),
            (r'cursor\.execute\s*\(\s*f["\']', 'SQL injection via f-string'),
            (r'query\s*=\s*["\'].*\+.*["\']', 'SQL injection via string concatenation'),
            (r'WHERE.*=.*\+', 'Potential SQL injection in WHERE clause'),
        ]

        # XSS patterns
        self.xss_patterns = [
            (r'innerHTML\s*=.*\+', 'XSS via innerHTML concatenation'),
            (r'document\.write\s*\(.*\+', 'XSS via document.write concatenation'),
            (r'eval\s*\(.*user', 'XSS via eval with user input'),
            (r'<script>.*\${', 'XSS via template literal in script tag'),
        ]

        # Hardcoded secrets patterns
        self.secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*["\'][A-Za-z0-9]{16,}["\']', 'Hardcoded API key'),
            (r'secret[_-]?key\s*=\s*["\'][A-Za-z0-9]{16,}["\']', 'Hardcoded secret key'),
            (r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded token'),
            (r'aws[_-]?access[_-]?key.*=\s*["\']AKIA[A-Z0-9]{16}["\']', 'AWS access key'),
        ]

        # Unsafe deserialization patterns
        self.deserialization_patterns = [
            (r'pickle\.loads?\s*\(', 'Unsafe pickle deserialization'),
            (r'yaml\.load\s*\(', 'Unsafe YAML deserialization'),
            (r'json\.loads?\s*\(.*input', 'Potentially unsafe JSON deserialization'),
            (r'eval\s*\(', 'Code injection via eval'),
            (r'exec\s*\(', 'Code injection via exec'),
        ]

        # AI-specific vulnerability patterns
        self.ai_specific_patterns = [
            (r'model\.load\s*\(.*input', 'Unsafe model loading from user input'),
            (r'torch\.load\s*\(.*request', 'Unsafe PyTorch model loading'),
            (r'joblib\.load\s*\(.*user', 'Unsafe joblib loading from user input'),
            (r'subprocess\.call\s*\(.*input', 'Command injection via subprocess'),
            (r'os\.system\s*\(.*\+', 'Command injection via os.system'),
        ]

    def scan_file(self, file_path: str, content: str) -> List[Issue]:
        """Scan a file for security vulnerabilities."""
        issues = []
        lines = content.splitlines()

        # Pattern-based scanning
        all_patterns = [
            ('sql_injection', self.sql_injection_patterns, 'high'),
            ('xss', self.xss_patterns, 'high'),
            ('secrets', self.secret_patterns, 'critical'),
            ('deserialization', self.deserialization_patterns, 'critical'),
            ('ai_specific', self.ai_specific_patterns, 'high'),
        ]

        for category, patterns, default_severity in all_patterns:
            if self._is_category_enabled(category):
                issues.extend(self._scan_patterns(file_path, lines, patterns, category, default_severity))

        # AST-based scanning for Python files
        if file_path.endswith('.py'):
            issues.extend(self._scan_python_ast(file_path, content))

        return issues

    def _scan_patterns(self, file_path: str, lines: List[str], patterns: List[tuple],
                      category: str, default_severity: str) -> List[Issue]:
        """Scan lines using regex patterns."""
        issues = []

        for line_num, line in enumerate(lines, 1):
            for pattern, description in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        severity=default_severity,
                        category='security',
                        message=f'{description}',
                        file_path=file_path,
                        line_number=line_num,
                        rule_id=f'security.{category}',
                        source_snippet=line.strip(),
                        suggestion=self._get_security_suggestion(category, description)
                    ))

        return issues

    def _scan_python_ast(self, file_path: str, content: str) -> List[Issue]:
        """Scan Python code using AST analysis."""
        issues = []

        try:
            tree = ast.parse(content)
            visitor = SecurityASTVisitor(file_path)
            visitor.visit(tree)
            issues.extend(visitor.issues)
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            issues.append(Issue(
                severity='low',
                category='security',
                message=f'AST analysis failed: {str(e)}',
                file_path=file_path,
                line_number=0,
                rule_id='security.ast_error'
            ))

        return issues

    def _is_category_enabled(self, category: str) -> bool:
        """Check if a security category is enabled in configuration."""
        category_map = {
            'sql_injection': 'check_sql_injection',
            'xss': 'check_xss',
            'secrets': 'check_hardcoded_secrets',
            'deserialization': 'check_unsafe_deserialization',
            'ai_specific': 'check_ai_vulnerabilities'
        }

        config_key = category_map.get(category, category)
        return self.config.get(f'security.{config_key}', True)

    def _get_security_suggestion(self, category: str, description: str) -> str:
        """Get security improvement suggestion."""
        suggestions = {
            'sql_injection': 'Use parameterized queries or ORM methods instead of string concatenation.',
            'xss': 'Sanitize user input and use safe DOM manipulation methods.',
            'secrets': 'Move secrets to environment variables or secure key management systems.',
            'deserialization': 'Validate input and use safe serialization formats like JSON.',
            'ai_specific': 'Validate file paths and sanitize inputs before loading models.',
        }

        for key, suggestion in suggestions.items():
            if key in category.lower():
                return suggestion

        return 'Review this code for potential security issues.'


class SecurityASTVisitor(ast.NodeVisitor):
    """AST visitor for Python security analysis."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []

    def visit_Call(self, node):
        """Visit function calls to detect security issues."""
        # Check for dangerous function calls
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            if func_name in ['eval', 'exec']:
                self.issues.append(Issue(
                    severity='critical',
                    category='security',
                    message=f'Dangerous use of {func_name}() function',
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule_id='security.dangerous_call',
                    suggestion=f'Avoid using {func_name}() with untrusted input. Use safer alternatives.'
                ))

        # Check for unsafe attribute access
        if isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr

            if attr_name == 'system' and isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'os':
                    self.issues.append(Issue(
                        severity='high',
                        category='security',
                        message='Use of os.system() can lead to command injection',
                        file_path=self.file_path,
                        line_number=node.lineno,
                        rule_id='security.command_injection',
                        suggestion='Use subprocess.run() with shell=False instead of os.system().'
                    ))

        self.generic_visit(node)

    def visit_Import(self, node):
        """Visit import statements to detect risky imports."""
        for alias in node.names:
            if alias.name in ['pickle', 'cPickle']:
                self.issues.append(Issue(
                    severity='medium',
                    category='security',
                    message='Import of pickle module detected - be careful with untrusted data',
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule_id='security.risky_import',
                    suggestion='Consider using safer serialization formats like JSON.'
                ))

        self.generic_visit(node)

    def visit_Str(self, node):
        """Visit string literals to detect hardcoded secrets."""
        # Check for potential secrets in string literals
        value = node.s if hasattr(node, 's') else ''

        if len(value) > 20 and re.match(r'^[A-Za-z0-9+/=]{20,}$', value):
            self.issues.append(Issue(
                severity='medium',
                category='security',
                message='Potential hardcoded secret detected',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='security.potential_secret',
                suggestion='Move secrets to environment variables or configuration files.'
            ))

        self.generic_visit(node)