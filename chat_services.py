#!/usr/bin/env python3
"""
Chat Service Abstractions
Provides interfaces for different chat services (Genesys, OpenAI-compatible, etc.)
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatResponse:
    """Represents a response from the chat service."""
    success: bool
    message: Optional[str] = None
    messages: Optional[List[ChatMessage]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseChatService(ABC):
    """Abstract base class for chat services."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the chat service.

        Args:
            config: Configuration dictionary for the service
        """
        self.config = config
        self.conversation_history: List[ChatMessage] = []

    @abstractmethod
    def start_session(self, initial_message: Optional[str] = None) -> bool:
        """Start a new chat session.

        Args:
            initial_message: Optional initial message to send

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def send_message(self, message: str, **kwargs) -> ChatResponse:
        """Send a message and get response.

        Args:
            message: Message text to send
            **kwargs: Additional service-specific parameters

        Returns:
            ChatResponse object
        """
        pass

    @abstractmethod
    def get_messages(self) -> List[ChatMessage]:
        """Get conversation history.

        Returns:
            List of ChatMessage objects
        """
        pass

    @abstractmethod
    def end_session(self) -> bool:
        """End the chat session.

        Returns:
            True if successful, False otherwise
        """
        pass

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to conversation history.

        Args:
            role: Message role (user/assistant/system)
            content: Message content
        """
        self.conversation_history.append(
            ChatMessage(role=role, content=content)
        )

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def get_history_as_openai_format(self) -> List[Dict[str, str]]:
        """Get conversation history in OpenAI API format.

        Returns:
            List of message dictionaries
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]
