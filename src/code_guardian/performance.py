"""Performance analyzer for detecting inefficient code patterns."""

import ast
import re
from typing import List, Tuple, Dict, Any
from pathlib import Path

from .models import Issue
from .config import Config


class PerformanceAnalyzer:
    """Analyzes code for performance issues commonly found in AI-generated code."""

    def __init__(self, config: Config):
        """Initialize the performance analyzer."""
        self.config = config
        self.max_complexity = config.get('performance.max_complexity', 10)

    def analyze_file(self, file_path: str, content: str) -> Tuple[List[Issue], float]:
        """Analyze a file for performance issues and return issues + score."""
        issues = []
        performance_score = 10.0  # Start with perfect score

        # Pattern-based analysis
        pattern_issues = self._analyze_patterns(file_path, content)
        issues.extend(pattern_issues)

        # AST-based analysis for Python files
        if file_path.endswith('.py'):
            ast_issues, complexity_score = self._analyze_python_ast(file_path, content)
            issues.extend(ast_issues)
            performance_score = min(performance_score, complexity_score)

        # JavaScript/TypeScript analysis
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            js_issues = self._analyze_javascript_patterns(file_path, content)
            issues.extend(js_issues)

        # Calculate performance score based on issues
        performance_score -= len([i for i in issues if i.severity == 'critical']) * 3
        performance_score -= len([i for i in issues if i.severity == 'high']) * 2
        performance_score -= len([i for i in issues if i.severity == 'medium']) * 1
        performance_score = max(0.0, performance_score)

        return issues, performance_score

    def _analyze_patterns(self, file_path: str, content: str) -> List[Issue]:
        """Analyze using regex patterns for common performance issues."""
        issues = []
        lines = content.splitlines()

        # Inefficient loop patterns
        inefficient_patterns = [
            (r'for.*in.*range\(len\(', 'Inefficient loop - use enumerate() or direct iteration', 'medium'),
            (r'while.*len\(.*\)\s*>', 'Inefficient while loop checking length', 'medium'),
            (r'\.append\(.*\)\s*\n.*for.*in', 'List comprehension may be more efficient', 'low'),
            (r'list\(filter\(.*list\(map\(', 'Nested list comprehension may be more efficient', 'medium'),
        ]

        # Memory usage patterns
        memory_patterns = [
            (r'.*\+=.*\[.*\]', 'Potential memory inefficiency with list concatenation', 'medium'),
            (r'.*\.copy\(\).*in.*loop', 'Copying in loop can cause memory issues', 'high'),
            (r'pd\.concat.*in.*for', 'Inefficient pandas concatenation in loop', 'high'),
            (r'np\.concatenate.*for.*in', 'Inefficient numpy concatenation in loop', 'medium'),
        ]

        # Database/IO patterns
        io_patterns = [
            (r'\.execute\(.*for.*in', 'Database queries in loop - consider batch operations', 'high'),
            (r'open\(.*for.*in', 'File operations in loop can be inefficient', 'medium'),
            (r'requests\.get\(.*for', 'HTTP requests in loop without session reuse', 'high'),
            (r'time\.sleep\(.*for', 'Sleep in loop may indicate inefficient design', 'low'),
        ]

        all_patterns = [
            *[(p, d, s) for p, d, s in inefficient_patterns],
            *[(p, d, s) for p, d, s in memory_patterns],
            *[(p, d, s) for p, d, s in io_patterns],
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, description, severity in all_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        severity=severity,
                        category='performance',
                        message=description,
                        file_path=file_path,
                        line_number=line_num,
                        rule_id='performance.pattern',
                        source_snippet=line.strip(),
                        suggestion=self._get_performance_suggestion(description)
                    ))

        return issues

    def _analyze_python_ast(self, file_path: str, content: str) -> Tuple[List[Issue], float]:
        """Analyze Python code using AST for complexity and performance issues."""
        issues = []
        complexity_score = 10.0

        try:
            tree = ast.parse(content)
            visitor = PerformanceASTVisitor(file_path, self.max_complexity)
            visitor.visit(tree)
            issues.extend(visitor.issues)
            complexity_score = visitor.get_complexity_score()
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            issues.append(Issue(
                severity='low',
                category='performance',
                message=f'AST analysis failed: {str(e)}',
                file_path=file_path,
                line_number=0,
                rule_id='performance.ast_error'
            ))

        return issues, complexity_score

    def _analyze_javascript_patterns(self, file_path: str, content: str) -> List[Issue]:
        """Analyze JavaScript/TypeScript for performance issues."""
        issues = []
        lines = content.splitlines()

        js_patterns = [
            (r'document\.getElementById.*in.*for', 'DOM queries in loop are inefficient', 'high'),
            (r'\.innerHTML\s*\+=', 'innerHTML concatenation causes reflow', 'medium'),
            (r'new.*RegExp.*in.*for', 'RegExp creation in loop is inefficient', 'medium'),
            (r'JSON\.parse.*JSON\.stringify', 'Deep clone via JSON is inefficient', 'medium'),
            (r'addEventListener.*in.*for', 'Event listeners in loop without cleanup', 'high'),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, description, severity in js_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        severity=severity,
                        category='performance',
                        message=description,
                        file_path=file_path,
                        line_number=line_num,
                        rule_id='performance.javascript',
                        source_snippet=line.strip()
                    ))

        return issues

    def _get_performance_suggestion(self, description: str) -> str:
        """Get performance improvement suggestions."""
        suggestions = {
            'inefficient loop': 'Use enumerate() or iterate directly over the collection.',
            'list comprehension': 'Consider using list comprehension for better performance.',
            'concatenation': 'Use join() for string concatenation or extend() for lists.',
            'database queries': 'Use batch operations or bulk inserts instead of individual queries.',
            'http requests': 'Use session objects to reuse connections.',
            'dom queries': 'Cache DOM elements outside of loops.',
            'memory inefficiency': 'Consider using generators or processing data in chunks.',
        }

        for key, suggestion in suggestions.items():
            if key.lower() in description.lower():
                return suggestion

        return 'Review this code for potential performance improvements.'


class PerformanceASTVisitor(ast.NodeVisitor):
    """AST visitor for Python performance analysis."""

    def __init__(self, file_path: str, max_complexity: int):
        self.file_path = file_path
        self.max_complexity = max_complexity
        self.issues = []
        self.function_complexities = []
        self.current_complexity = 0
        self.nested_loops = 0

    def visit_FunctionDef(self, node):
        """Visit function definitions to analyze complexity."""
        # Save current state
        old_complexity = self.current_complexity
        self.current_complexity = 1  # Base complexity

        # Visit function body
        self.generic_visit(node)

        # Check complexity
        if self.current_complexity > self.max_complexity:
            self.issues.append(Issue(
                severity='medium' if self.current_complexity <= self.max_complexity * 1.5 else 'high',
                category='performance',
                message=f'Function complexity ({self.current_complexity}) exceeds threshold ({self.max_complexity})',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='performance.complexity',
                suggestion='Consider breaking this function into smaller functions.'
            ))

        self.function_complexities.append(self.current_complexity)
        self.current_complexity = old_complexity

    def visit_For(self, node):
        """Visit for loops to detect nested loops and inefficiencies."""
        self.current_complexity += 1
        old_nested = self.nested_loops
        self.nested_loops += 1

        # Check for nested loops
        if self.nested_loops > 2:
            self.issues.append(Issue(
                severity='medium',
                category='performance',
                message=f'Deeply nested loops (depth: {self.nested_loops}) may cause performance issues',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='performance.nested_loops',
                suggestion='Consider flattening the loop structure or using more efficient algorithms.'
            ))

        # Check for inefficient patterns
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                if len(node.iter.args) == 1:
                    if isinstance(node.iter.args[0], ast.Call):
                        func = node.iter.args[0].func
                        if isinstance(func, ast.Name) and func.id == 'len':
                            self.issues.append(Issue(
                                severity='low',
                                category='performance',
                                message='Use enumerate() or direct iteration instead of range(len())',
                                file_path=self.file_path,
                                line_number=node.lineno,
                                rule_id='performance.range_len',
                                suggestion='Use "for i, item in enumerate(collection)" or "for item in collection".'
                            ))

        self.generic_visit(node)
        self.nested_loops = old_nested

    def visit_While(self, node):
        """Visit while loops."""
        self.current_complexity += 1
        self.nested_loops += 1
        self.generic_visit(node)
        self.nested_loops -= 1

    def visit_If(self, node):
        """Visit if statements."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        """Visit try statements."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        """Visit with statements."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_ListComp(self, node):
        """Visit list comprehensions."""
        # Check for nested comprehensions
        if any(isinstance(gen.iter, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp))
               for gen in node.generators):
            self.issues.append(Issue(
                severity='medium',
                category='performance',
                message='Nested list comprehensions can be hard to read and maintain',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='performance.nested_comprehension',
                suggestion='Consider breaking into separate comprehensions or using traditional loops.'
            ))

        self.generic_visit(node)

    def visit_Call(self, node):
        """Visit function calls to detect performance issues."""
        # Check for inefficient function calls
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'append' and self.nested_loops > 0:
                self.issues.append(Issue(
                    severity='low',
                    category='performance',
                    message='List.append() in nested loop may be inefficient',
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule_id='performance.append_in_loop',
                    suggestion='Consider using list comprehension or preallocating the list.'
                ))

        self.generic_visit(node)

    def get_complexity_score(self) -> float:
        """Calculate complexity score."""
        if not self.function_complexities:
            return 10.0

        avg_complexity = sum(self.function_complexities) / len(self.function_complexities)
        max_complexity = max(self.function_complexities)

        # Score based on average and maximum complexity
        score = 10.0
        score -= max(0, (avg_complexity - self.max_complexity) * 0.5)
        score -= max(0, (max_complexity - self.max_complexity * 1.5) * 0.3)

        return max(0.0, score)