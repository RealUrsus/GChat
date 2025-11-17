"""Custom exceptions for Genesys Web Chat API client."""

from typing import Any, Dict, List, Optional


class GenesysChatError(Exception):
    """Base exception for all Genesys Chat errors."""

    pass


class GenesysChatAPIError(GenesysChatError):
    """Raised when API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            errors: List of error details from API response
        """
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)

    def __str__(self) -> str:
        """String representation of the error."""
        error_details = ""
        if self.errors:
            error_details = ", ".join(
                f"{err.get('code')}: {err.get('message')}"
                for err in self.errors
            )
            return f"{super().__str__()} - Errors: {error_details}"
        return super().__str__()


class GenesysChatConnectionError(GenesysChatError):
    """Raised when connection to the API fails."""

    pass


class GenesysChatValidationError(GenesysChatError):
    """Raised when input validation fails."""

    pass


class GenesysChatTimeoutError(GenesysChatError):
    """Raised when a request times out."""

    pass


class GenesysChatAuthenticationError(GenesysChatError):
    """Raised when authentication fails."""

    pass
