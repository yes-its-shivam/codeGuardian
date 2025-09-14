"""Tests for the security scanner."""

import pytest
from code_guardian.scanner import SecurityScanner
from code_guardian.config import Config


def test_security_scanner_initialization():
    """Test security scanner initialization."""
    config = Config()
    scanner = SecurityScanner(config)
    assert scanner.config is config


def test_sql_injection_detection():
    """Test SQL injection pattern detection."""
    config = Config()
    scanner = SecurityScanner(config)

    # Test code with SQL injection vulnerability
    vulnerable_code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)
'''

    issues = scanner.scan_file('test.py', vulnerable_code)
    sql_issues = [issue for issue in issues if 'injection' in issue.message.lower()]
    assert len(sql_issues) > 0


def test_hardcoded_secret_detection():
    """Test hardcoded secret detection."""
    config = Config()
    scanner = SecurityScanner(config)

    # Test code with hardcoded secrets - FAKE KEYS FOR TESTING ONLY
    vulnerable_code = '''
def connect_to_api():
    api_key = "sk_test_FAKE_DEMO_KEY_NOT_REAL_123456789abc"
    password = "demo_password_VULNERABLE_TEST_EXAMPLE"
    return api_key, password
'''

    issues = scanner.scan_file('test.py', vulnerable_code)
    secret_issues = [issue for issue in issues if 'secret' in issue.message.lower() or 'password' in issue.message.lower()]
    assert len(secret_issues) > 0


def test_eval_detection():
    """Test detection of dangerous eval() usage."""
    config = Config()
    scanner = SecurityScanner(config)

    # Test code with eval
    vulnerable_code = '''
def process_input(user_input):
    result = eval(user_input)
    return result
'''

    issues = scanner.scan_file('test.py', vulnerable_code)
    eval_issues = [issue for issue in issues if 'eval' in issue.message.lower()]
    assert len(eval_issues) > 0


def test_pickle_import_detection():
    """Test detection of risky pickle imports."""
    config = Config()
    scanner = SecurityScanner(config)

    # Test code with pickle import
    code_with_pickle = '''
import pickle
import json

def load_data(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data
'''

    issues = scanner.scan_file('test.py', code_with_pickle)
    pickle_issues = [issue for issue in issues if 'pickle' in issue.message.lower()]
    assert len(pickle_issues) > 0


def test_safe_code_no_issues():
    """Test that safe code produces no security issues."""
    config = Config()
    scanner = SecurityScanner(config)

    # Safe code
    safe_code = '''
def get_user_safely(user_id):
    """Safely retrieve user by ID using parameterized query."""
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, [user_id])

def process_data(data):
    """Process data safely."""
    return json.loads(data)
'''

    issues = scanner.scan_file('test.py', safe_code)
    # Should have minimal or no critical security issues
    critical_issues = [issue for issue in issues if issue.severity == 'critical']
    assert len(critical_issues) == 0


def test_category_disabling():
    """Test disabling security categories."""
    config_dict = {
        'security': {
            'enabled': True,
            'check_sql_injection': False,
            'check_hardcoded_secrets': False
        }
    }
    config = Config(config_dict)
    scanner = SecurityScanner(config)

    # This should not trigger SQL injection detection when disabled
    vulnerable_code = '''
api_key = "sk_live_1234567890abcdef"
query = "SELECT * FROM users WHERE id = " + user_id
'''

    issues = scanner.scan_file('test.py', vulnerable_code)

    # Should have fewer issues when categories are disabled
    sql_issues = [issue for issue in issues if 'injection' in issue.message.lower()]
    secret_issues = [issue for issue in issues if 'secret' in issue.message.lower()]

    # These should be empty since we disabled the checks
    assert len(sql_issues) == 0
    assert len(secret_issues) == 0