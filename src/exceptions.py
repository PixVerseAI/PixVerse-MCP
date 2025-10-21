"""
Custom exceptions for Pixverse MCP.
"""

from typing import Any, Dict, Optional


class PixverseError(Exception):
    """Base exception for all Pixverse-related errors."""

    def __init__(self, message: str, error_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class PixverseAPIError(PixverseError):
    """Raised when the Pixverse API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, response_data)
        self.status_code = status_code
        self.response_data = response_data or {}


class PixverseAuthError(PixverseError):
    """Raised when authentication fails."""

    pass


class PixverseRateLimitError(PixverseError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class PixverseValidationError(PixverseError):
    """Raised when request validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field


class PixverseTimeoutError(PixverseError):
    """Raised when a request times out."""

    pass


class PixverseConnectionError(PixverseError):
    """Raised when connection to Pixverse API fails."""

    pass
