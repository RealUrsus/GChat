"""Genesys Web Chat v2 API Client.

A Python client for interacting with the Genesys Web Chat v2 API.
"""

__version__ = "2.0.0"
__author__ = "Your Name"

from .client import GenesysChatClient
from .models import (
    ChatOperationResult,
    Event,
    EventType,
    Participant,
    WebAPIErrorInfo,
)
from .exceptions import (
    GenesysChatError,
    GenesysChatAPIError,
    GenesysChatConnectionError,
)

__all__ = [
    "GenesysChatClient",
    "ChatOperationResult",
    "Event",
    "EventType",
    "Participant",
    "WebAPIErrorInfo",
    "GenesysChatError",
    "GenesysChatAPIError",
    "GenesysChatConnectionError",
]
