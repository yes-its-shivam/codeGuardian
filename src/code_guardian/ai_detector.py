"""AI pattern detector for identifying AI-generated code."""

import re
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass

from .config import Config


@dataclass
class AIPattern:
    """Represents a detected AI pattern."""
    pattern_type: str
    confidence: float
    description: str
    line_number: int
    evidence: str


class AIPatternDetector:
    """Detects patterns commonly found in AI-generated code."""

    def __init__(self, config: Config):
        """Initialize the AI pattern detector."""
        self.config = config
        self.confidence_threshold = config.get('ai_detection.confidence_threshold', 0.7)
        self._init_patterns()

    def _init_patterns(self):
        """Initialize AI detection patterns."""
        # Comment patterns that indicate AI generation
        self.comment_patterns = [
            (r'#\s*(This|Here)\s+is\s+(a|an)\s+', 0.8, 'AI-style explanatory comment'),
            (r'#\s*Note:\s*', 0.7, 'AI-style note comment'),
            (r'#\s*Important:\s*', 0.7, 'AI-style important comment'),
            (r'#\s*Example:\s*', 0.6, 'AI-style example comment'),
            (r'#\s*TODO:\s*Implement\s+', 0.5, 'Generic TODO comment'),
            (r'#\s*(Initialize|Create|Define)\s+(the|a)\s+', 0.7, 'AI-style action comment'),
            (r'/\*\*\s*\n\s*\*\s*(This|Here)', 0.8, 'AI-style JSDoc comment'),
        ]

        # Code patterns that suggest AI generation
        self.code_patterns = [
            (r'if\s+.*\s+is\s+not\s+None\s*:', 0.6, 'Verbose None check'),
            (r'\.format\(\s*\)', 0.5, 'Empty format() call'),
            (r'print\s*\(\s*f?["\'].*\{.*\}.*["\']\s*\)', 0.4, 'Debug print statement'),
            (r'import\s+sys\s*\n.*sys\.path\.append', 0.7, 'Manual path manipulation'),
            (r'try:\s*\n.*except\s+Exception\s+as\s+e:\s*\n.*print', 0.6, 'Generic exception handling'),
            (r'def\s+main\s*\(\s*\)\s*:', 0.5, 'Generic main function'),
            (r'if\s+__name__\s*==\s*["\']__main__["\']:', 0.4, 'Standard main guard'),
        ]

        # Variable naming patterns
        self.naming_patterns = [
            (r'\bdata\b', 0.6, 'Generic "data" variable name'),
            (r'\bresult\b', 0.5, 'Generic "result" variable name'),
            (r'\bvalue\b', 0.5, 'Generic "value" variable name'),
            (r'\bitem\b', 0.4, 'Generic "item" variable name'),
            (r'\btemp\b', 0.6, 'Generic "temp" variable name'),
            (r'\bmy_\w+', 0.7, 'AI-style "my_" prefixed variables'),
        ]

        # Function/class naming patterns
        self.structure_patterns = [
            (r'class\s+MyClass\s*[\(:]', 0.9, 'Generic "MyClass" class name'),
            (r'def\s+my_function\s*\(', 0.9, 'Generic "my_function" function name'),
            (r'def\s+calculate_\w+\s*\(', 0.6, 'AI-style calculate_ function'),
            (r'def\s+process_\w+\s*\(', 0.6, 'AI-style process_ function'),
            (r'def\s+handle_\w+\s*\(', 0.6, 'AI-style handle_ function'),
        ]

        # Import patterns
        self.import_patterns = [
            (r'import\s+os\s*\n.*import\s+sys\s*\n.*import\s+json', 0.7, 'Common AI import sequence'),
            (r'from\s+typing\s+import\s+List,\s*Dict,\s*Any', 0.6, 'Common typing imports'),
            (r'import\s+\w+\s+as\s+\w{1,2}\s*\n', 0.5, 'Short alias imports'),
        ]

        # String patterns
        self.string_patterns = [
            (r'["\']Hello,?\s+World!?["\']', 0.8, 'Hello World string'),
            (r'["\']This\s+is\s+a\s+test["\']', 0.7, 'Test string'),
            (r'["\']Enter\s+\w+:', 0.6, 'Input prompt string'),
            (r'["\']Processing\s+\w+\.\.\.["\']', 0.6, 'Processing message'),
        ]

    def detect_ai_patterns(self, content: str, file_path: str = "") -> Tuple[float, List[AIPattern]]:
        """Detect AI patterns in code content."""
        detected_patterns = []
        lines = content.splitlines()
        total_confidence = 0.0

        # Check comment patterns
        patterns = self._detect_comment_patterns(lines)
        detected_patterns.extend(patterns)

        # Check code structure patterns
        patterns = self._detect_code_patterns(lines)
        detected_patterns.extend(patterns)

        # Check naming patterns
        patterns = self._detect_naming_patterns(lines)
        detected_patterns.extend(patterns)

        # Check import patterns
        patterns = self._detect_import_patterns(content)
        detected_patterns.extend(patterns)

        # Check string patterns
        patterns = self._detect_string_patterns(lines)
        detected_patterns.extend(patterns)

        # Calculate overall confidence
        if detected_patterns:
            # Weight patterns by confidence and normalize
            confidence_scores = [p.confidence for p in detected_patterns]
            # Use weighted average with diminishing returns for multiple patterns
            total_confidence = min(0.95, sum(confidence_scores) / (len(confidence_scores) + 2))
        else:
            total_confidence = 0.0

        # Filter patterns above threshold
        filtered_patterns = [p for p in detected_patterns if p.confidence >= self.confidence_threshold]

        return total_confidence, filtered_patterns

    def _detect_comment_patterns(self, lines: List[str]) -> List[AIPattern]:
        """Detect AI patterns in comments."""
        patterns = []

        for line_num, line in enumerate(lines, 1):
            for pattern, confidence, description in self.comment_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    patterns.append(AIPattern(
                        pattern_type='comment',
                        confidence=confidence,
                        description=description,
                        line_number=line_num,
                        evidence=line.strip()
                    ))

        return patterns

    def _detect_code_patterns(self, lines: List[str]) -> List[AIPattern]:
        """Detect AI patterns in code structure."""
        patterns = []

        for line_num, line in enumerate(lines, 1):
            # Structure patterns
            for pattern, confidence, description in self.structure_patterns:
                if re.search(pattern, line):
                    patterns.append(AIPattern(
                        pattern_type='structure',
                        confidence=confidence,
                        description=description,
                        line_number=line_num,
                        evidence=line.strip()
                    ))

            # General code patterns
            for pattern, confidence, description in self.code_patterns:
                if re.search(pattern, line):
                    patterns.append(AIPattern(
                        pattern_type='code',
                        confidence=confidence,
                        description=description,
                        line_number=line_num,
                        evidence=line.strip()
                    ))

        return patterns

    def _detect_naming_patterns(self, lines: List[str]) -> List[AIPattern]:
        """Detect AI patterns in variable/function naming."""
        patterns = []

        for line_num, line in enumerate(lines, 1):
            for pattern, confidence, description in self.naming_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    patterns.append(AIPattern(
                        pattern_type='naming',
                        confidence=confidence,
                        description=description,
                        line_number=line_num,
                        evidence=line.strip()
                    ))

        return patterns

    def _detect_import_patterns(self, content: str) -> List[AIPattern]:
        """Detect AI patterns in import statements."""
        patterns = []

        for pattern, confidence, description in self.import_patterns:
            if re.search(pattern, content, re.MULTILINE):
                # Find the line number of the first import
                lines = content.splitlines()
                for line_num, line in enumerate(lines, 1):
                    if 'import' in line:
                        patterns.append(AIPattern(
                            pattern_type='imports',
                            confidence=confidence,
                            description=description,
                            line_number=line_num,
                            evidence=line.strip()
                        ))
                        break

        return patterns

    def _detect_string_patterns(self, lines: List[str]) -> List[AIPattern]:
        """Detect AI patterns in string literals."""
        patterns = []

        for line_num, line in enumerate(lines, 1):
            for pattern, confidence, description in self.string_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    patterns.append(AIPattern(
                        pattern_type='strings',
                        confidence=confidence,
                        description=description,
                        line_number=line_num,
                        evidence=line.strip()
                    ))

        return patterns

    def analyze_code_style(self, content: str) -> Dict[str, Any]:
        """Analyze overall code style for AI generation indicators."""
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]

        if not non_empty_lines:
            return {}

        style_metrics = {
            'avg_line_length': sum(len(line) for line in non_empty_lines) / len(non_empty_lines),
            'comment_ratio': len([line for line in lines if line.strip().startswith('#')]) / len(lines),
            'empty_line_ratio': len([line for line in lines if not line.strip()]) / len(lines),
            'docstring_present': '"""' in content or "'''" in content,
            'type_hints_present': ': ' in content and '->' in content,
        }

        # AI code often has specific style characteristics
        ai_indicators = {}

        # Very consistent formatting (AI tends to be very consistent)
        line_lengths = [len(line) for line in non_empty_lines]
        if line_lengths:
            length_variance = sum((x - style_metrics['avg_line_length']) ** 2 for x in line_lengths) / len(line_lengths)
            ai_indicators['consistent_formatting'] = length_variance < 100  # Low variance

        # High comment ratio (AI often over-comments)
        ai_indicators['over_commented'] = style_metrics['comment_ratio'] > 0.3

        # Perfect spacing (AI tends to be very consistent with spacing)
        spacing_patterns = len(re.findall(r'=\s+\w+', content)) + len(re.findall(r'\w+\s+=', content))
        total_assignments = len(re.findall(r'=', content))
        if total_assignments > 0:
            ai_indicators['perfect_spacing'] = spacing_patterns / total_assignments > 0.8

        return {**style_metrics, **ai_indicators}