"""
Custom exception hierarchy for the Adaptive Memory Python SDK.
"""

from typing import Optional, Any, Dict


class AdaptiveMemoryError(Exception):
    """Base exception for all Adaptive Memory SDK errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class ConnectionError(AdaptiveMemoryError):
    """Raised when communication with the Adaptive Memory API fails."""
    pass


class NotFoundError(AdaptiveMemoryError):
    """Raised when a requested resource (e.g. memory) does not exist."""
    pass


class ValidationError(AdaptiveMemoryError):
    """Raised when invalid request parameters or payload are provided."""
    pass


class AuthenticationError(AdaptiveMemoryError):
    """Raised when authentication with the API fails."""
    pass


class ServerError(AdaptiveMemoryError):
    """Raised when the remote server encounters an internal error."""
    pass
