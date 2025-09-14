#!/usr/bin/env python3
"""
Example of well-written, secure code that follows best practices.
This demonstrates what good code looks like to Code Guardian.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import sqlite3
from contextlib import contextmanager

# Configuration through environment variables (not hardcoded)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants with meaningful names
MAX_QUERY_RESULTS = 1000
DEFAULT_PAGE_SIZE = 50
HASH_ALGORITHM = 'sha256'


class DatabaseManager:
    """Manages database connections and operations securely."""

    def __init__(self, db_path: str):
        """Initialize database manager with connection path."""
        self.db_path = db_path
        self._ensure_db_exists()

    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()

    def _ensure_db_exists(self) -> None:
        """Ensure database and required tables exist."""
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()


class UserRepository:
    """Repository for user data operations with security best practices."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository with database manager."""
        self.db_manager = db_manager

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Retrieve user by ID using parameterized query to prevent SQL injection.

        Args:
            user_id: The user ID to look up

        Returns:
            User data dictionary or None if not found
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # Safe parameterized query - prevents SQL injection
                cursor.execute(
                    "SELECT id, username, email, created_at FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Database error retrieving user {user_id}: {e}")
            return None

    def create_user(self, username: str, email: str, password: str) -> Optional[int]:
        """
        Create new user with secure password handling.

        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)

        Returns:
            User ID if successful, None otherwise
        """
        try:
            password_hash = self._hash_password(password)

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash)
                )
                conn.commit()
                return cursor.lastrowid

        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed - username or email already exists")
            return None
        except sqlite3.Error as e:
            logger.error(f"Database error creating user: {e}")
            return None

    def _hash_password(self, password: str) -> str:
        """
        Securely hash password using SHA-256.
        In production, use bcrypt or Argon2 instead.
        """
        # Add salt for better security
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode('utf-8'),
            salt,
            100000  # iterations
        )
        return salt.hex() + password_hash.hex()


class DataProcessor:
    """Efficient data processing with good performance practices."""

    @staticmethod
    def process_items_efficiently(items: List[str]) -> List[str]:
        """
        Process items efficiently using list comprehension and best practices.

        Args:
            items: List of strings to process

        Returns:
            Processed list of strings
        """
        if not items:
            return []

        # Use list comprehension for efficiency instead of loops
        processed = [item.upper().strip() for item in items if item.strip()]

        # Filter and transform in single pass
        return [item for item in processed if len(item) > 0]

    @staticmethod
    def batch_process_data(data: List[Dict], batch_size: int = DEFAULT_PAGE_SIZE) -> List[Dict]:
        """
        Process data in batches for better memory usage.

        Args:
            data: List of data items to process
            batch_size: Size of each processing batch

        Returns:
            Processed data
        """
        results = []

        # Process in batches to avoid memory issues
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            processed_batch = [DataProcessor._transform_item(item) for item in batch]
            results.extend(processed_batch)

        return results

    @staticmethod
    def _transform_item(item: Dict) -> Dict:
        """Transform a single data item."""
        return {
            'id': item.get('id'),
            'processed': True,
            'timestamp': item.get('timestamp')
        }


class ConfigurationManager:
    """Manages application configuration securely."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_path = Path(config_path) if config_path else Path('config.json')
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file or environment."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load config from {self.config_path}: {e}")

        # Fallback to environment variables
        return {
            'database_url': os.getenv('DATABASE_URL', 'sqlite:///app.db'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'max_connections': int(os.getenv('MAX_CONNECTIONS', '10'))
        }

    def get(self, key: str, default=None) -> Union[str, int, bool, None]:
        """Get configuration value safely."""
        return self._config.get(key, default)


def validate_user_input(user_input: str, max_length: int = 255) -> bool:
    """
    Validate user input safely without using eval or exec.

    Args:
        user_input: User provided input string
        max_length: Maximum allowed length

    Returns:
        True if input is valid, False otherwise
    """
    if not user_input or not isinstance(user_input, str):
        return False

    if len(user_input) > max_length:
        return False

    # Check for potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", ';', '--']
    return not any(char in user_input for char in dangerous_chars)


def safe_file_operations(file_path: str, data: str) -> bool:
    """
    Demonstrate safe file operations with proper error handling.

    Args:
        file_path: Path to file
        data: Data to write

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)

        # Validate file path to prevent directory traversal
        if '..' in str(path) or str(path).startswith('/'):
            logger.warning(f"Potentially dangerous file path: {file_path}")
            return False

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file safely with encoding specified
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)

        logger.info(f"Successfully wrote data to {file_path}")
        return True

    except OSError as e:
        logger.error(f"File operation failed: {e}")
        return False


def main() -> int:
    """
    Main application entry point with proper error handling.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Initialize components
        config = ConfigurationManager()
        db_manager = DatabaseManager(config.get('database_url'))
        user_repo = UserRepository(db_manager)

        # Example operations
        sample_data = ['item1', 'item2', 'item3']
        processed_data = DataProcessor.process_items_efficiently(sample_data)

        logger.info(f"Processed {len(processed_data)} items successfully")

        # Example user creation with validation
        test_username = "test_user"
        test_email = "test@example.com"
        test_password = "secure_password_123"

        if validate_user_input(test_username) and validate_user_input(test_email):
            user_id = user_repo.create_user(test_username, test_email, test_password)
            if user_id:
                logger.info(f"Created user with ID: {user_id}")

        return 0

    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)