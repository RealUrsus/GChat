"""Unit tests for data models."""

import unittest
from genesys_chat.models import (
    ChatOperationResult,
    Event,
    EventType,
    Participant,
    WebAPIErrorInfo,
)


class TestParticipant(unittest.TestCase):
    """Test Participant model."""

    def test_from_dict(self):
        """Test creating Participant from dictionary."""
        data = {
            "nickname": "Agent Smith",
            "participantId": 123,
            "type": "Agent",
        }

        participant = Participant.from_dict(data)

        self.assertEqual(participant.nickname, "Agent Smith")
        self.assertEqual(participant.participant_id, 123)
        self.assertEqual(participant.type, "Agent")

    def test_to_dict(self):
        """Test converting Participant to dictionary."""
        participant = Participant(
            nickname="John Doe", participant_id=456, type="Client"
        )

        data = participant.to_dict()

        self.assertEqual(data["nickname"], "John Doe")
        self.assertEqual(data["participantId"], 456)
        self.assertEqual(data["type"], "Client")


class TestEvent(unittest.TestCase):
    """Test Event model."""

    def test_from_dict_message(self):
        """Test creating Message event from dictionary."""
        data = {
            "type": "Message",
            "index": 1,
            "text": "Hello, world!",
            "messageType": "text",
            "from": {
                "nickname": "Agent",
                "participantId": 1,
                "type": "Agent",
            },
            "utcTime": 1234567890,
            "userData": {"key": "value"},
            "eventAttributes": {"attr": "value"},
        }

        event = Event.from_dict(data)

        self.assertEqual(event.type, EventType.MESSAGE)
        self.assertEqual(event.index, 1)
        self.assertEqual(event.text, "Hello, world!")
        self.assertIsNotNone(event.from_participant)
        self.assertEqual(event.from_participant.nickname, "Agent")
        self.assertEqual(event.utc_time, 1234567890)

    def test_from_dict_unknown_type(self):
        """Test creating event with unknown type."""
        data = {"type": "UnknownEventType"}

        event = Event.from_dict(data)

        self.assertEqual(event.type, EventType.UNKNOWN)

    def test_to_dict(self):
        """Test converting Event to dictionary."""
        participant = Participant(nickname="Agent", participant_id=1, type="Agent")

        event = Event(
            type=EventType.MESSAGE,
            index=1,
            text="Test message",
            message_type="text",
            from_participant=participant,
            utc_time=1234567890,
        )

        data = event.to_dict()

        self.assertEqual(data["type"], "Message")
        self.assertEqual(data["index"], 1)
        self.assertEqual(data["text"], "Test message")
        self.assertIn("from", data)


class TestWebAPIErrorInfo(unittest.TestCase):
    """Test WebAPIErrorInfo model."""

    def test_from_dict(self):
        """Test creating error from dictionary."""
        data = {"code": 100, "message": "MISSED_PARAMETER", "advice": "Check params"}

        error = WebAPIErrorInfo.from_dict(data)

        self.assertEqual(error.code, 100)
        self.assertEqual(error.message, "MISSED_PARAMETER")
        self.assertEqual(error.advice, "Check params")

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = WebAPIErrorInfo(code=200, message="ERROR", advice="Fix it")

        data = error.to_dict()

        self.assertEqual(data["code"], 200)
        self.assertEqual(data["message"], "ERROR")
        self.assertEqual(data["advice"], "Fix it")


class TestChatOperationResult(unittest.TestCase):
    """Test ChatOperationResult model."""

    def test_from_dict_success(self):
        """Test creating successful result from dictionary."""
        data = {
            "statusCode": 0,
            "chatId": "chat123",
            "secureKey": "key123",
            "userId": "user123",
            "alias": "alias123",
            "nextPosition": 5,
            "messages": [
                {"type": "Message", "text": "Hello"},
            ],
            "errors": [],
            "chatEnded": False,
            "monitored": True,
            "userData": {"lang": "en"},
        }

        result = ChatOperationResult.from_dict(data)

        self.assertEqual(result.status_code, 0)
        self.assertEqual(result.chat_id, "chat123")
        self.assertEqual(result.secure_key, "key123")
        self.assertEqual(result.user_id, "user123")
        self.assertEqual(result.next_position, 5)
        self.assertEqual(len(result.messages), 1)
        self.assertEqual(len(result.errors), 0)
        self.assertTrue(result.is_success)

    def test_from_dict_with_errors(self):
        """Test creating result with errors from dictionary."""
        data = {
            "statusCode": 1,
            "errors": [
                {"code": 100, "message": "ERROR"},
            ],
        }

        result = ChatOperationResult.from_dict(data)

        self.assertEqual(result.status_code, 1)
        self.assertEqual(len(result.errors), 1)
        self.assertFalse(result.is_success)

    def test_is_success_property(self):
        """Test is_success property."""
        # Success case
        result1 = ChatOperationResult(status_code=0, errors=[])
        self.assertTrue(result1.is_success)

        # Error case - non-zero status
        result2 = ChatOperationResult(status_code=1, errors=[])
        self.assertFalse(result2.is_success)

        # Error case - has errors
        error = WebAPIErrorInfo(code=100, message="ERROR")
        result3 = ChatOperationResult(status_code=0, errors=[error])
        self.assertFalse(result3.is_success)


if __name__ == "__main__":
    unittest.main()
