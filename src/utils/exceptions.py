"""Custom exceptions for Eng2SQL services."""
from __future__ import annotations


class Eng2SQLError(Exception):
    """Base exception for all Eng2SQL errors."""


class SQLGenerationError(Eng2SQLError):
    """Raised when the SQL generation service fails."""


class SchemaDetectionError(Eng2SQLError):
    """Raised when schema detection or loading fails."""


class QueryExecutionError(Eng2SQLError):
    """Raised when executing a SQL query against the database fails."""


class DatabaseConnectionError(Eng2SQLError):
    """Raised when establishing a database connection fails."""


class ConfigurationError(Eng2SQLError):
    """Raised when the application configuration is invalid or incomplete."""
