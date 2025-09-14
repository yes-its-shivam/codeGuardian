"""Configuration management for AI Code Guardian."""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class Config:
    """Configuration manager for AI Code Guardian."""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize configuration with default values."""
        self._config = config_dict or self._get_default_config()

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'version': 1,
            'security': {
                'enabled': True,
                'severity_threshold': 'medium',
                'check_sql_injection': True,
                'check_xss': True,
                'check_hardcoded_secrets': True,
                'check_unsafe_deserialization': True,
            },
            'performance': {
                'enabled': True,
                'check_complexity': True,
                'check_memory_usage': True,
                'check_inefficient_loops': True,
                'max_complexity': 10,
            },
            'maintainability': {
                'enabled': True,
                'max_complexity': 10,
                'max_function_length': 50,
                'max_class_methods': 20,
                'check_naming_conventions': True,
            },
            'ai_detection': {
                'enabled': True,
                'confidence_threshold': 0.7,
                'check_comment_patterns': True,
                'check_code_patterns': True,
            },
            'exclude': [
                '*.pyc',
                '__pycache__/',
                '.git/',
                'node_modules/',
                'venv/',
                '.env',
                '*.min.js',
                '*.min.css',
            ],
            'reporting': {
                'include_source_snippets': True,
                'max_issues_per_file': 20,
                'show_ai_confidence': True,
            }
        }

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file."""
        if config_path:
            path = Path(config_path)
        else:
            # Look for config in current directory
            for filename in ['.ai-guardian.yml', '.ai-guardian.yaml', 'ai-guardian.yml']:
                path = Path(filename)
                if path.exists():
                    break
            else:
                # No config file found, use defaults
                return cls()

        try:
            with open(path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return cls(config_data)
        except (yaml.YAMLError, FileNotFoundError, PermissionError) as e:
            raise ValueError(f"Failed to load configuration from {path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @property
    def security_enabled(self) -> bool:
        """Check if security scanning is enabled."""
        return self.get('security.enabled', True)

    @property
    def performance_enabled(self) -> bool:
        """Check if performance analysis is enabled."""
        return self.get('performance.enabled', True)

    @property
    def maintainability_enabled(self) -> bool:
        """Check if maintainability scoring is enabled."""
        return self.get('maintainability.enabled', True)

    @property
    def ai_detection_enabled(self) -> bool:
        """Check if AI pattern detection is enabled."""
        return self.get('ai_detection.enabled', True)

    @property
    def exclude_patterns(self) -> List[str]:
        """Get list of exclude patterns."""
        return self.get('exclude', [])

    @property
    def security_threshold(self) -> str:
        """Get security severity threshold."""
        return self.get('security.severity_threshold', 'medium')

    @property
    def max_complexity(self) -> int:
        """Get maximum allowed complexity."""
        return self.get('performance.max_complexity', 10)

    @property
    def ai_confidence_threshold(self) -> float:
        """Get AI detection confidence threshold."""
        return self.get('ai_detection.confidence_threshold', 0.7)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._config.copy()

    def save(self, path: str) -> None:
        """Save configuration to file."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, indent=2)