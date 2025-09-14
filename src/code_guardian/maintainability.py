"""Maintainability scorer for code quality assessment."""

import ast
import re
from typing import List, Tuple, Dict, Any
from collections import defaultdict

from .models import Issue
from .config import Config


class MaintainabilityScorer:
    """Analyzes code maintainability and readability."""

    def __init__(self, config: Config):
        """Initialize the maintainability scorer."""
        self.config = config
        self.max_complexity = config.get('maintainability.max_complexity', 10)
        self.max_function_length = config.get('maintainability.max_function_length', 50)
        self.max_class_methods = config.get('maintainability.max_class_methods', 20)

    def score_file(self, file_path: str, content: str) -> Tuple[List[Issue], float]:
        """Score a file for maintainability and return issues + score."""
        issues = []
        base_score = 10.0

        # Pattern-based analysis
        pattern_issues = self._analyze_patterns(file_path, content)
        issues.extend(pattern_issues)

        # AST-based analysis for Python files
        if file_path.endswith('.py'):
            ast_issues, structural_score = self._analyze_python_structure(file_path, content)
            issues.extend(ast_issues)
            base_score = min(base_score, structural_score)

        # Calculate final score based on issues
        final_score = base_score
        final_score -= len([i for i in issues if i.severity == 'critical']) * 2
        final_score -= len([i for i in issues if i.severity == 'high']) * 1.5
        final_score -= len([i for i in issues if i.severity == 'medium']) * 1
        final_score -= len([i for i in issues if i.severity == 'low']) * 0.5

        return issues, max(0.0, final_score)

    def _analyze_patterns(self, file_path: str, content: str) -> List[Issue]:
        """Analyze code patterns that affect maintainability."""
        issues = []
        lines = content.splitlines()

        # Check for code smells
        for line_num, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 120:
                issues.append(Issue(
                    severity='low',
                    category='maintainability',
                    message=f'Line too long ({len(line)} characters)',
                    file_path=file_path,
                    line_number=line_num,
                    rule_id='maintainability.line_length',
                    suggestion='Break long lines into multiple lines for better readability.'
                ))

            # Too many parameters (simple heuristic)
            if 'def ' in line and line.count(',') > 5:
                issues.append(Issue(
                    severity='medium',
                    category='maintainability',
                    message='Function has too many parameters',
                    file_path=file_path,
                    line_number=line_num,
                    rule_id='maintainability.too_many_params',
                    suggestion='Consider using a configuration object or breaking the function apart.'
                ))

            # Magic numbers
            magic_number_pattern = r'\b\d{2,}\b'
            if re.search(magic_number_pattern, line) and 'def ' not in line:
                if not re.search(r'#.*\d+', line):  # Skip if commented
                    issues.append(Issue(
                        severity='low',
                        category='maintainability',
                        message='Magic number detected - consider using named constants',
                        file_path=file_path,
                        line_number=line_num,
                        rule_id='maintainability.magic_number',
                        suggestion='Replace magic numbers with named constants.'
                    ))

            # TODO/FIXME comments
            if re.search(r'#.*\b(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
                issues.append(Issue(
                    severity='low',
                    category='maintainability',
                    message='TODO/FIXME comment found',
                    file_path=file_path,
                    line_number=line_num,
                    rule_id='maintainability.todo_comment',
                    suggestion='Address TODO/FIXME comments before deployment.'
                ))

            # Deeply nested code (simple heuristic)
            leading_whitespace = len(line) - len(line.lstrip())
            if leading_whitespace > 24:  # More than 6 levels of indentation
                issues.append(Issue(
                    severity='medium',
                    category='maintainability',
                    message='Code is too deeply nested',
                    file_path=file_path,
                    line_number=line_num,
                    rule_id='maintainability.deep_nesting',
                    suggestion='Consider extracting nested code into separate functions.'
                ))

        return issues

    def _analyze_python_structure(self, file_path: str, content: str) -> Tuple[List[Issue], float]:
        """Analyze Python code structure using AST."""
        issues = []
        structural_score = 10.0

        try:
            tree = ast.parse(content)
            visitor = MaintainabilityASTVisitor(
                file_path, self.max_complexity, self.max_function_length, self.max_class_methods
            )
            visitor.visit(tree)
            issues.extend(visitor.issues)
            structural_score = visitor.get_structural_score()
        except SyntaxError:
            issues.append(Issue(
                severity='high',
                category='maintainability',
                message='Syntax error in file',
                file_path=file_path,
                line_number=0,
                rule_id='maintainability.syntax_error',
                suggestion='Fix syntax errors to improve code maintainability.'
            ))
            structural_score = 5.0
        except Exception as e:
            issues.append(Issue(
                severity='low',
                category='maintainability',
                message=f'Structure analysis failed: {str(e)}',
                file_path=file_path,
                line_number=0,
                rule_id='maintainability.analysis_error'
            ))

        return issues, structural_score


class MaintainabilityASTVisitor(ast.NodeVisitor):
    """AST visitor for maintainability analysis."""

    def __init__(self, file_path: str, max_complexity: int, max_function_length: int, max_class_methods: int):
        self.file_path = file_path
        self.max_complexity = max_complexity
        self.max_function_length = max_function_length
        self.max_class_methods = max_class_methods
        self.issues = []

        # Metrics tracking
        self.function_lengths = []
        self.function_complexities = []
        self.class_method_counts = []
        self.variable_names = []
        self.function_names = []
        self.class_names = []

        # Current context
        self.current_complexity = 0
        self.current_function_length = 0

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        # Check naming convention
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
            self.issues.append(Issue(
                severity='low',
                category='maintainability',
                message=f'Class name "{node.name}" doesn\'t follow PascalCase convention',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.class_naming',
                suggestion='Use PascalCase for class names (e.g., MyClass).'
            ))

        self.class_names.append(node.name)

        # Count methods in class
        method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
        if method_count > self.max_class_methods:
            self.issues.append(Issue(
                severity='medium',
                category='maintainability',
                message=f'Class has too many methods ({method_count})',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.too_many_methods',
                suggestion='Consider splitting the class or using composition.'
            ))

        self.class_method_counts.append(method_count)

        # Check for missing docstring
        if not ast.get_docstring(node):
            self.issues.append(Issue(
                severity='low',
                category='maintainability',
                message=f'Class "{node.name}" missing docstring',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.missing_docstring',
                suggestion='Add a docstring to explain the class purpose.'
            ))

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        # Check naming convention
        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
            self.issues.append(Issue(
                severity='low',
                category='maintainability',
                message=f'Function name "{node.name}" doesn\'t follow snake_case convention',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.function_naming',
                suggestion='Use snake_case for function names (e.g., my_function).'
            ))

        self.function_names.append(node.name)

        # Check function length
        function_end = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 10
        function_length = function_end - node.lineno
        if function_length > self.max_function_length:
            self.issues.append(Issue(
                severity='medium',
                category='maintainability',
                message=f'Function is too long ({function_length} lines)',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.long_function',
                suggestion='Break long functions into smaller, focused functions.'
            ))

        self.function_lengths.append(function_length)

        # Check parameter count
        param_count = len(node.args.args)
        if param_count > 5:
            self.issues.append(Issue(
                severity='medium',
                category='maintainability',
                message=f'Function has too many parameters ({param_count})',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.too_many_params',
                suggestion='Consider using a configuration object or reducing parameters.'
            ))

        # Check for missing docstring (except for very short functions)
        if function_length > 5 and not ast.get_docstring(node) and not node.name.startswith('_'):
            self.issues.append(Issue(
                severity='low',
                category='maintainability',
                message=f'Function "{node.name}" missing docstring',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.missing_docstring',
                suggestion='Add a docstring to explain the function purpose and parameters.'
            ))

        # Analyze complexity
        old_complexity = self.current_complexity
        self.current_complexity = 1
        self.generic_visit(node)

        if self.current_complexity > self.max_complexity:
            self.issues.append(Issue(
                severity='medium',
                category='maintainability',
                message=f'Function complexity ({self.current_complexity}) is too high',
                file_path=self.file_path,
                line_number=node.lineno,
                rule_id='maintainability.high_complexity',
                suggestion='Simplify the function by extracting complex logic into helper functions.'
            ))

        self.function_complexities.append(self.current_complexity)
        self.current_complexity = old_complexity

    def visit_Name(self, node):
        """Visit variable names to check naming conventions."""
        if isinstance(node.ctx, ast.Store):  # Variable assignment
            name = node.id
            if len(name) == 1 and name not in ['i', 'j', 'k', 'x', 'y', 'z']:
                self.issues.append(Issue(
                    severity='low',
                    category='maintainability',
                    message=f'Single-letter variable name "{name}" is not descriptive',
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule_id='maintainability.short_variable_name',
                    suggestion='Use descriptive variable names instead of single letters.'
                ))

            # Check for non-conventional naming
            if re.match(r'^[A-Z][A-Z0-9_]*$', name):  # ALL_CAPS
                if not name.isupper() or '_' not in name:
                    self.issues.append(Issue(
                        severity='low',
                        category='maintainability',
                        message=f'Constant "{name}" should use UPPER_CASE convention',
                        file_path=self.file_path,
                        line_number=node.lineno,
                        rule_id='maintainability.constant_naming'
                    ))

            self.variable_names.append(name)

        self.generic_visit(node)

    def visit_If(self, node):
        """Visit if statements for complexity."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        """Visit for loops for complexity."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        """Visit while loops for complexity."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        """Visit try statements for complexity."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        """Visit with statements for complexity."""
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Visit boolean operations for complexity."""
        self.current_complexity += len(node.values) - 1
        self.generic_visit(node)

    def get_structural_score(self) -> float:
        """Calculate structural score based on metrics."""
        score = 10.0

        # Function length penalty
        if self.function_lengths:
            avg_length = sum(self.function_lengths) / len(self.function_lengths)
            if avg_length > self.max_function_length:
                score -= (avg_length - self.max_function_length) * 0.1

        # Complexity penalty
        if self.function_complexities:
            avg_complexity = sum(self.function_complexities) / len(self.function_complexities)
            if avg_complexity > self.max_complexity:
                score -= (avg_complexity - self.max_complexity) * 0.2

        # Class size penalty
        if self.class_method_counts:
            avg_methods = sum(self.class_method_counts) / len(self.class_method_counts)
            if avg_methods > self.max_class_methods:
                score -= (avg_methods - self.max_class_methods) * 0.1

        return max(0.0, score)