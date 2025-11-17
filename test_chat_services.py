#!/usr/bin/env python3
"""
Test script for chat services
Tests the chat service abstractions with a mock service
"""

import sys
from typing import Dict, List, Optional, Any
from chat_services import BaseChatService, ChatMessage, ChatResponse

class MockChatService(BaseChatService):
    """Mock chat service for testing."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.session_active = False
        self.message_count = 0

    def start_session(self, initial_message: Optional[str] = None) -> bool:
        """Start mock session."""
        print("🚀 Starting mock chat session")
        self.session_active = True
        if initial_message:
            self.add_to_history("user", initial_message)
            # Mock assistant response
            self.add_to_history("assistant", f"Mock response to: {initial_message}")
        return True

    def send_message(self, message: str, **kwargs) -> ChatResponse:
        """Send message and get mock response."""
        if not self.session_active:
            return ChatResponse(success=False, error="Session not active")

        self.message_count += 1
        self.add_to_history("user", message)

        # Generate mock response
        mock_response = f"Mock assistant response #{self.message_count} to: {message[:30]}..."

        self.add_to_history("assistant", mock_response)

        return ChatResponse(
            success=True,
            message=mock_response,
            messages=self.get_messages()
        )

    def get_messages(self) -> List[ChatMessage]:
        """Get conversation history."""
        return self.conversation_history

    def end_session(self) -> bool:
        """End mock session."""
        if not self.session_active:
            return False
        print(f"👋 Ending mock session ({self.message_count} messages)")
        self.session_active = False
        return True


def test_mock_service():
    """Test mock chat service."""
    print("Testing MockChatService...")
    print("=" * 60)

    # Create service
    config = {"test": "config"}
    service = MockChatService(config)

    # Start session
    assert service.start_session("Hello!"), "Failed to start session"
    print("✅ Session started")

    # Send messages
    messages_to_send = [
        "How are you?",
        "Tell me about your features",
        "Thank you!"
    ]

    for msg in messages_to_send:
        response = service.send_message(msg)
        assert response.success, f"Failed to send message: {msg}"
        print(f"✅ Sent: {msg}")
        print(f"   Got: {response.message}")

    # Check history
    history = service.get_messages()
    print(f"\n📊 Conversation history: {len(history)} messages")
    for i, msg in enumerate(history, 1):
        print(f"  [{i}] {msg.role}: {msg.content[:50]}...")

    # End session
    assert service.end_session(), "Failed to end session"
    print("\n✅ Session ended")

    print("=" * 60)
    print("✅ MockChatService test passed!\n")


def test_conversation_history():
    """Test conversation history functionality."""
    print("Testing conversation history...")
    print("=" * 60)

    config = {}
    service = MockChatService(config)
    service.start_session()

    # Add messages
    service.add_to_history("user", "First message")
    service.add_to_history("assistant", "First response")
    service.add_to_history("user", "Second message")
    service.add_to_history("assistant", "Second response")

    # Get OpenAI format
    openai_format = service.get_history_as_openai_format()
    print(f"OpenAI format history: {len(openai_format)} messages")
    for msg in openai_format:
        print(f"  {msg['role']}: {msg['content']}")

    # Test clear history
    service.clear_history()
    assert len(service.conversation_history) == 0, "History not cleared"
    print("\n✅ History cleared successfully")

    service.end_session()
    print("=" * 60)
    print("✅ Conversation history test passed!\n")


def main():
    """Run tests."""
    print("\n🧪 Running chat service tests\n")

    try:
        test_mock_service()
        test_conversation_history()
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
