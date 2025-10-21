"""
Pixverse MCP - Model Context Protocol server for Pixverse video generation APIs.

This package provides a comprehensive interface to Pixverse's video generation
capabilities through the Model Context Protocol (MCP).
"""

__version__ = "0.2.2"
__author__ = "Pixverse Team"
__email__ = "dev@pixverse.ai"

from .client import PixverseClient
from .exceptions import (
    PixverseAPIError,
    PixverseAuthError,
    PixverseError,
    PixverseRateLimitError,
    PixverseValidationError,
)

__all__ = [
    "PixverseClient",
    "PixverseError",
    "PixverseAPIError",
    "PixverseAuthError",
    "PixverseRateLimitError",
    "PixverseValidationError",
]
