"""Excepciones personalizadas para herramientas."""
from typing import Any


class HerramientasError(Exception):
    """Base exception for all herramientas errors."""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class FileNotFoundError(HerramientasError):
    """Raised when a required file cannot be found."""
    pass


class UnsupportedFormatError(HerramientasError):
    """Raised when file format is not supported."""
    pass


class ProcessingError(HerramientasError):
    """Raised when processing fails."""
    pass


class TimeoutError(HerramientasError):
    """Raised when operation exceeds time limit."""
    pass


class ValidationError(HerramientasError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(HerramientasError):
    """Raised when configuration is invalid."""
    pass