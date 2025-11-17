#!/usr/bin/env python3
"""
Conversation Source Abstractions
Provides different sources for conversation messages (files, external services, etc.)
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Iterator
from pathlib import Path
from chat_services import BaseChatService, ChatResponse

logger = logging.getLogger(__name__)


class ConversationSource(ABC):
    """Abstract base class for conversation sources."""

    @abstractmethod
    def get_messages(self) -> Iterator[str]:
        """Get messages from the source.

        Yields:
            Message strings
        """
        pass

    @abstractmethod
    def has_messages(self) -> bool:
        """Check if source has more messages.

        Returns:
            True if more messages available
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the source to beginning."""
        pass


class FileConversationSource(ConversationSource):
    """Load conversations from a local file."""

    def __init__(self, file_path: str):
        """Initialize file conversation source.

        Args:
            file_path: Path to file with messages (one per line)
        """
        self.file_path = Path(file_path)
        self.messages: List[str] = []
        self.current_index = 0
        self._load_messages()

    def _load_messages(self) -> None:
        """Load messages from file."""
        logger.info(f"📖 Loading conversation from: {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.messages = [line.strip() for line in f if line.strip()]
            logger.info(f"✅ Loaded {len(self.messages)} messages from file")
        except FileNotFoundError:
            logger.error(f"❌ File not found: {self.file_path}")
            self.messages = []
        except Exception as e:
            logger.error(f"❌ Error loading file: {e}")
            self.messages = []

    def get_messages(self) -> Iterator[str]:
        """Get messages from file.

        Yields:
            Message strings
        """
        while self.current_index < len(self.messages):
            message = self.messages[self.current_index]
            self.current_index += 1
            yield message

    def has_messages(self) -> bool:
        """Check if source has more messages.

        Returns:
            True if more messages available
        """
        return self.current_index < len(self.messages)

    def reset(self) -> None:
        """Reset to beginning of file."""
        self.current_index = 0
        logger.info("🔄 Reset file conversation source")

    def get_total_count(self) -> int:
        """Get total number of messages.

        Returns:
            Total message count
        """
        return len(self.messages)

    def get_current_index(self) -> int:
        """Get current message index.

        Returns:
            Current index
        """
        return self.current_index


class ExternalServiceConversationSource(ConversationSource):
    """Get conversations from an external chat service."""

    def __init__(
        self,
        chat_service: BaseChatService,
        initial_prompts: Optional[List[str]] = None,
        max_turns: int = 10,
        context_mode: bool = True
    ):
        """Initialize external service conversation source.

        Args:
            chat_service: BaseChatService implementation
            initial_prompts: Optional list of prompts to start conversation
            max_turns: Maximum number of conversation turns
            context_mode: If True, maintain context between messages
        """
        self.chat_service = chat_service
        self.initial_prompts = initial_prompts or [
            "Hello! Let's have a conversation.",
            "Can you help me with something?",
            "Tell me something interesting."
        ]
        self.max_turns = max_turns
        self.context_mode = context_mode
        self.current_turn = 0
        self.generated_messages: List[str] = []
        self.prompt_index = 0

        logger.info("🌐 Initialized external service conversation source")
        logger.info(f"   Context mode: {'enabled' if context_mode else 'disabled'}")
        logger.info(f"   Max turns: {max_turns}")

    def get_messages(self) -> Iterator[str]:
        """Get messages from external service.

        Yields:
            Message strings (alternating between prompts and generated responses)
        """
        while self.current_turn < self.max_turns:
            # Get next prompt
            if self.prompt_index < len(self.initial_prompts):
                prompt = self.initial_prompts[self.prompt_index]
                self.prompt_index += 1
            else:
                # Generate contextual follow-up based on conversation
                if self.generated_messages:
                    prompt = self._generate_followup()
                else:
                    break

            yield prompt
            self.current_turn += 1

            # Get response from external service
            if self.has_messages():
                response = self.chat_service.send_message(prompt)
                if response.success and response.message:
                    self.generated_messages.append(response.message)
                    yield response.message
                    self.current_turn += 1

    def _generate_followup(self) -> str:
        """Generate a contextual follow-up prompt.

        Returns:
            Follow-up prompt string
        """
        followups = [
            "Can you tell me more about that?",
            "That's interesting. What else?",
            "I see. Can you elaborate?",
            "Thanks! What would you recommend?",
            "Interesting perspective. Any other thoughts?"
        ]
        index = (self.current_turn // 2) % len(followups)
        return followups[index]

    def has_messages(self) -> bool:
        """Check if source has more messages.

        Returns:
            True if more messages available
        """
        return self.current_turn < self.max_turns

    def reset(self) -> None:
        """Reset the conversation source."""
        self.current_turn = 0
        self.generated_messages = []
        self.prompt_index = 0
        if not self.context_mode:
            self.chat_service.clear_history()
        logger.info("🔄 Reset external service conversation source")


class HybridConversationSource(ConversationSource):
    """Hybrid source that combines file prompts with external service responses."""

    def __init__(
        self,
        file_path: str,
        chat_service: BaseChatService,
        get_responses: bool = True
    ):
        """Initialize hybrid conversation source.

        Args:
            file_path: Path to file with user prompts
            chat_service: BaseChatService implementation for responses
            get_responses: If True, get AI responses to each prompt
        """
        self.file_source = FileConversationSource(file_path)
        self.chat_service = chat_service
        self.get_responses = get_responses

        logger.info("🔀 Initialized hybrid conversation source")
        logger.info(f"   File: {file_path}")
        logger.info(f"   Get responses: {get_responses}")

    def get_messages(self) -> Iterator[str]:
        """Get messages from hybrid source.

        Yields:
            Message strings (file prompts + AI responses)
        """
        for prompt in self.file_source.get_messages():
            # Yield the user prompt from file
            yield prompt

            # Get and yield AI response if enabled
            if self.get_responses:
                response = self.chat_service.send_message(prompt)
                if response.success and response.message:
                    yield response.message

    def has_messages(self) -> bool:
        """Check if source has more messages.

        Returns:
            True if more messages available
        """
        return self.file_source.has_messages()

    def reset(self) -> None:
        """Reset the hybrid source."""
        self.file_source.reset()
        self.chat_service.clear_history()
        logger.info("🔄 Reset hybrid conversation source")
