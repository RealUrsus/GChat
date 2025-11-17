#!/usr/bin/env python3
"""
External Chat Service Implementation
Supports OpenAI-compatible APIs (OpenAI, Groq, Together AI, etc.)
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from chat_services import BaseChatService, ChatMessage, ChatResponse

logger = logging.getLogger(__name__)


class ExternalChatService(BaseChatService):
    """External chat service using OpenAI-compatible API."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize external chat service.

        Args:
            config: Configuration dictionary with keys:
                - api_key: API key for authentication
                - base_url: Base URL for API (e.g., https://api.openai.com/v1)
                - model: Model name (e.g., gpt-3.5-turbo, llama-3.1-8b-instant)
                - system_prompt: Optional system prompt
                - temperature: Sampling temperature (0.0-2.0)
                - max_tokens: Maximum tokens in response
        """
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.system_prompt = config.get('system_prompt', 'You are a helpful assistant.')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 500)
        self.timeout = config.get('timeout', 30)
        self.session_active = False

        # Build chat completions endpoint
        self.chat_url = f"{self.base_url.rstrip('/')}/chat/completions"

        logger.info(f"🌐 Initialized external chat service:")
        logger.info(f"   Base URL: {self.base_url}")
        logger.info(f"   Model: {self.model}")

    def start_session(self, initial_message: Optional[str] = None) -> bool:
        """Start a new chat session.

        Args:
            initial_message: Optional initial message to send

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting external chat session")
        logger.info("=" * 60)

        # Clear history and add system prompt
        self.clear_history()
        self.add_to_history("system", self.system_prompt)

        # Send initial message if provided
        if initial_message:
            response = self.send_message(initial_message)
            if not response.success:
                logger.error("❌ Failed to start session with initial message")
                return False

        self.session_active = True
        logger.info("✅ External chat session started successfully")
        return True

    def send_message(self, message: str, **kwargs) -> ChatResponse:
        """Send a message and get response from external service.

        Args:
            message: Message text to send
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            ChatResponse object
        """
        if not self.api_key:
            error = "API key not configured"
            logger.error(f"❌ {error}")
            return ChatResponse(success=False, error=error)

        # Add user message to history
        self.add_to_history("user", message)
        logger.info(f"💬 User: {message[:60]}{'...' if len(message) > 60 else ''}")

        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self.get_history_as_openai_format(),
            "temperature": kwargs.get('temperature', self.temperature),
            "max_tokens": kwargs.get('max_tokens', self.max_tokens)
        }

        try:
            # Make API request
            response = requests.post(
                self.chat_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()

                # Extract assistant's response
                assistant_message = data['choices'][0]['message']['content']
                self.add_to_history("assistant", assistant_message)

                logger.info(f"🤖 Assistant: {assistant_message[:60]}{'...' if len(assistant_message) > 60 else ''}")

                return ChatResponse(
                    success=True,
                    message=assistant_message,
                    messages=self.get_messages(),
                    metadata={
                        'model': data.get('model'),
                        'usage': data.get('usage', {})
                    }
                )
            else:
                error = f"API request failed: {response.status_code} - {response.text[:200]}"
                logger.error(f"❌ {error}")
                return ChatResponse(success=False, error=error)

        except requests.exceptions.Timeout:
            error = "Request timeout"
            logger.error(f"❌ {error}")
            return ChatResponse(success=False, error=error)

        except requests.exceptions.RequestException as e:
            error = f"Request exception: {str(e)}"
            logger.error(f"❌ {error}")
            return ChatResponse(success=False, error=error)

        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            logger.error(f"❌ {error}")
            return ChatResponse(success=False, error=error)

    def get_messages(self) -> List[ChatMessage]:
        """Get conversation history.

        Returns:
            List of ChatMessage objects
        """
        return self.conversation_history

    def end_session(self) -> bool:
        """End the chat session.

        Returns:
            True if successful, False otherwise
        """
        if not self.session_active:
            logger.warning("No active session to end")
            return False

        logger.info("👋 Ending external chat session")
        logger.info(f"📊 Total messages: {len(self.conversation_history)}")
        self.session_active = False
        return True


class GroqChatService(ExternalChatService):
    """Groq-specific chat service implementation."""

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant", **kwargs):
        """Initialize Groq chat service.

        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.1-8b-instant)
            **kwargs: Additional configuration
        """
        config = {
            'api_key': api_key,
            'base_url': 'https://api.groq.com/openai/v1',
            'model': model,
            **kwargs
        }
        super().__init__(config)
        logger.info("🚀 Using Groq API")


class OpenAIChatService(ExternalChatService):
    """OpenAI-specific chat service implementation."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        """Initialize OpenAI chat service.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-3.5-turbo)
            **kwargs: Additional configuration
        """
        config = {
            'api_key': api_key,
            'base_url': 'https://api.openai.com/v1',
            'model': model,
            **kwargs
        }
        super().__init__(config)
        logger.info("🚀 Using OpenAI API")


class TogetherAIChatService(ExternalChatService):
    """Together AI-specific chat service implementation."""

    def __init__(self, api_key: str, model: str = "meta-llama/Llama-3-8b-chat-hf", **kwargs):
        """Initialize Together AI chat service.

        Args:
            api_key: Together AI API key
            model: Model name
            **kwargs: Additional configuration
        """
        config = {
            'api_key': api_key,
            'base_url': 'https://api.together.xyz/v1',
            'model': model,
            **kwargs
        }
        super().__init__(config)
        logger.info("🚀 Using Together AI API")
