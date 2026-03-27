import os
import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from typing import Optional, Dict, Any
from contextlib import contextmanager

class DatabaseConnection:
    """
    MySQL database connection manager with connection pooling.

    This class provides a reusable database connection interface
    with proper error handling and connection pooling for better performance.
    """

    def __init__(self):
        """Initialize database connection with environment variables."""
        self.pool = None
        self._load_config()
        self._create_pool()

    def _load_config(self) -> None:
        """
        Load database configuration from environment variables.

        Raises:
            ValueError: If required environment variables are missing.
        """
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']

        self.config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,  # We'll manage transactions manually
            'pool_name': 'alertwave_pool',
            'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
            'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', '10'))
        }

        # Check for missing required variables
        missing_vars = [var for var in required_vars if not self.config.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def _create_pool(self) -> None:
        """
        Create MySQL connection pool.

        Raises:
            mysql.connector.Error: If pool creation fails.
        """
        try:
            self.pool = MySQLConnectionPool(**self.config)
            print(f"✅ Database connection pool created successfully (size: {self.config['pool_size']})")
        except Error as e:
            raise Error(f"Failed to create connection pool: {e}")

    def get_connection(self):
        """
        Get a connection from the pool.

        Returns:
            MySQLConnection: Database connection object.

        Raises:
            mysql.connector.Error: If connection cannot be obtained.
        """
        if not self.pool:
            raise Error("Connection pool not initialized")

        try:
            return self.pool.get_connection()
        except Error as e:
            raise Error(f"Failed to get connection from pool: {e}")

    @contextmanager
    def get_cursor(self, dictionary: bool = True):
        """
        Context manager for database cursor operations.

        Args:
            dictionary (bool): If True, returns results as dictionaries.
                              If False, returns results as tuples.

        Yields:
            MySQLCursor: Database cursor object.

        Raises:
            mysql.connector.Error: If cursor operations fail.
        """
        connection = None
        cursor = None

        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            yield cursor

            # Commit transaction if no exceptions
            connection.commit()

        except Error as e:
            # Rollback on error
            if connection:
                connection.rollback()
            raise Error(f"Database operation failed: {e}")

        finally:
            # Always close cursor and return connection to pool
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def execute_query(self, query: str, params: Optional[tuple] = None,
                     fetch: bool = True, dictionary: bool = True) -> Optional[list]:
        """
        Execute a database query with automatic connection management.

        Args:
            query (str): SQL query to execute.
            params (tuple, optional): Query parameters.
            fetch (bool): Whether to fetch results (for SELECT queries).
            dictionary (bool): Return results as dictionaries.

        Returns:
            list or None: Query results if fetch=True, None otherwise.

        Raises:
            mysql.connector.Error: If query execution fails.
        """
        with self.get_cursor(dictionary=dictionary) as cursor:
            cursor.execute(query, params or ())

            if fetch:
                return cursor.fetchall()
            else:
                return None

    def execute_many(self, query: str, params_list: list) -> None:
        """
        Execute a query multiple times with different parameters.

        Args:
            query (str): SQL query to execute.
            params_list (list): List of parameter tuples.

        Raises:
            mysql.connector.Error: If query execution fails.
        """
        with self.get_cursor(dictionary=False) as cursor:
            cursor.executemany(query, params_list)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return connection info.

        Returns:
            Dict[str, Any]: Connection test results.
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT VERSION() as version, DATABASE() as database")
                result = cursor.fetchone()

                return {
                    "status": "success",
                    "message": "Database connection successful",
                    "version": result.get("version"),
                    "database": result.get("database"),
                    "pool_size": self.config['pool_size']
                }

        except Error as e:
            return {
                "status": "error",
                "message": f"Database connection failed: {str(e)}"
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection.

        Returns:
            Dict[str, Any]: Health check results.
        """
        try:
            # Simple query to test connectivity
            result = self.execute_query("SELECT 1 as health_check")
            if result and result[0].get("health_check") == 1:
                return {
                    "status": "healthy",
                    "message": "Database is responding correctly"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Database health check failed"
                }

        except Error as e:
            return {
                "status": "unhealthy",
                "message": f"Database health check error: {str(e)}"
            }

# Global database instance
_db_instance = None

def get_database() -> DatabaseConnection:
    """
    Get the global database connection instance (Singleton pattern).

    Returns:
        DatabaseConnection: Database connection instance.

    Raises:
        RuntimeError: If database is not initialized.
    """
    global _db_instance
    if _db_instance is None:
        try:
            _db_instance = DatabaseConnection()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database: {e}")
    return _db_instance