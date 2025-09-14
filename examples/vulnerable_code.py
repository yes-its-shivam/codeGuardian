#!/usr/bin/env python3
"""
Example of vulnerable code that Code Guardian should detect.
This file contains intentional security vulnerabilities for testing purposes.
"""

import os
import pickle
import subprocess
import sqlite3
from typing import Any, Dict


# Security Issue: Hardcoded secrets - EXAMPLE VULNERABLE CODE FOR DEMO ONLY
API_KEY = "sk_test_FAKE_KEY_FOR_DEMO_PURPOSES_ONLY_123456789"
DATABASE_PASSWORD = "demo_password_VULNERABLE_EXAMPLE_NOT_REAL"
SECRET_TOKEN = "demo_jwt_FAKE_TOKEN_FOR_TESTING_PURPOSES_ONLY"


def get_user_data(user_id: str) -> Dict[str, Any]:
    """
    Security Issue: SQL injection vulnerability
    Performance Issue: Database query in potential loop context
    """
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)  # Vulnerable to SQL injection
    return cursor.fetchone()


def process_user_input(user_input: str) -> Any:
    """
    Security Issue: Code injection via eval
    """
    # This is dangerous - eval can execute arbitrary code
    result = eval(user_input)
    return result


def load_user_data(data_file: str) -> Any:
    """
    Security Issue: Unsafe deserialization with pickle
    """
    with open(data_file, 'rb') as f:
        # Pickle can execute arbitrary code during deserialization
        data = pickle.load(f)
    return data


def execute_system_command(command: str) -> str:
    """
    Security Issue: Command injection via os.system
    """
    # This is vulnerable to command injection
    os.system(f"ls -la {command}")

    # This is also vulnerable
    subprocess.call(f"grep {command} /etc/passwd", shell=True)

    return "Command executed"


def inefficient_data_processing(data_list: list) -> list:
    """
    Performance Issues: Multiple inefficiencies
    Maintainability Issues: Poor naming and structure
    """
    # Performance Issue: Inefficient loop with range(len())
    result = []
    for i in range(len(data_list)):
        item = data_list[i]

        # Performance Issue: String concatenation in loop
        processed = ""
        for char in str(item):
            processed += char.upper()

        # Performance Issue: List append in nested loop
        for j in range(len(processed)):
            if j % 2 == 0:
                result.append(processed[j])

    return result


class MyClass:  # Maintainability Issue: Generic class name
    """
    This class has maintainability issues.
    Note: This is a generic comment that AI often generates.
    """

    def __init__(self):
        # Maintainability Issue: Magic numbers
        self.max_items = 100
        self.timeout = 30
        self.buffer_size = 1024

    def my_function(self, data, value, item, result, temp, x, y, z):
        """
        Maintainability Issues:
        - Too many parameters
        - Generic parameter names
        - Generic function name
        """
        # Performance Issue: Nested loops with high complexity
        for i in range(len(data)):
            for j in range(len(value)):
                for k in range(len(item)):
                    if data[i] == value[j] and value[j] == item[k]:
                        # Performance Issue: Inefficient operations
                        temp_list = []
                        temp_list.append(result)
                        x = temp_list.copy()  # Unnecessary copy
                        y = str(x) + str(z)  # String concatenation

        return temp

    def calculate_something(self, input_data):
        """Calculate something - generic AI comment."""
        # TODO: Implement this function properly
        pass

    def process_data(self, my_data):
        """Process the data - another generic comment."""
        # FIXME: This is a temporary hack
        return my_data

    def handle_request(self, request_data):
        """Handle the incoming request."""
        # Magic number without explanation
        if len(request_data) > 500:
            return None
        return request_data


def main():
    """
    Main function with AI-style patterns.
    Here is an example of how to use this code.
    """
    # AI Pattern: Generic variable names
    data = [1, 2, 3, 4, 5]
    result = inefficient_data_processing(data)

    # Security Issue: Using hardcoded secrets
    user_data = get_user_data("'; DROP TABLE users; --")

    # AI Pattern: Print statement for debugging
    print(f"Processing complete: {result}")

    return result


if __name__ == "__main__":
    main()