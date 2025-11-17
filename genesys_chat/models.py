"""Data models for Genesys Web Chat v2 API.

These models are based on the OpenAPI specification and provide
type-safe representations of API requests and responses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(str, Enum):
    """Event types in chat session."""

    PARTICIPANT_JOINED = "ParticipantJoined"
    PARTICIPANT_LEFT = "ParticipantLeft"
    MESSAGE = "Message"
    TYPING_STARTED = "TypingStarted"
    TYPING_STOPPED = "TypingStopped"
    NICKNAME_UPDATED = "NicknameUpdated"
    PUSH_URL = "PushUrl"
    FILE_UPLOADED = "FileUploaded"
    FILE_DELETED = "FileDeleted"
    CUSTOM_NOTICE = "CustomNotice"
    NOTICE = "Notice"
    IDLE_ALERT = "IdleAlert"
    IDLE_CLOSE = "IdleClose"
    UNKNOWN = "Unknown"


@dataclass
class Participant:
    """Represents a chat participant."""

    nickname: Optional[str] = None
    participant_id: Optional[int] = None
    type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Participant":
        """Create Participant from dictionary."""
        return cls(
            nickname=data.get("nickname"),
            participant_id=data.get("participantId"),
            type=data.get("type"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Participant to dictionary."""
        return {
            "nickname": self.nickname,
            "participantId": self.participant_id,
            "type": self.type,
        }


@dataclass
class Event:
    """Represents a chat event."""

    type: EventType
    index: Optional[int] = None
    text: Optional[str] = None
    message_type: Optional[str] = None
    from_participant: Optional[Participant] = None
    utc_time: Optional[int] = None
    user_data: Dict[str, str] = field(default_factory=dict)
    event_attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create Event from dictionary."""
        event_type_str = data.get("type", "Unknown")
        try:
            event_type = EventType(event_type_str)
        except ValueError:
            event_type = EventType.UNKNOWN

        from_participant = None
        if "from" in data:
            from_participant = Participant.from_dict(data["from"])

        return cls(
            type=event_type,
            index=data.get("index"),
            text=data.get("text"),
            message_type=data.get("messageType"),
            from_participant=from_participant,
            utc_time=data.get("utcTime"),
            user_data=data.get("userData", {}),
            event_attributes=data.get("eventAttributes", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Event to dictionary."""
        result: Dict[str, Any] = {
            "type": self.type.value,
            "index": self.index,
            "text": self.text,
            "messageType": self.message_type,
            "utcTime": self.utc_time,
            "userData": self.user_data,
            "eventAttributes": self.event_attributes,
        }
        if self.from_participant:
            result["from"] = self.from_participant.to_dict()
        return result


@dataclass
class WebAPIErrorInfo:
    """Represents an API error."""

    code: int
    message: str
    advice: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebAPIErrorInfo":
        """Create WebAPIErrorInfo from dictionary."""
        return cls(
            code=data.get("code", 0),
            message=data.get("message", ""),
            advice=data.get("advice"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert WebAPIErrorInfo to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "advice": self.advice,
        }


@dataclass
class ChatOperationResult:
    """Represents the result of a chat operation."""

    status_code: int = 0
    chat_id: Optional[str] = None
    secure_key: Optional[str] = None
    user_id: Optional[str] = None
    alias: Optional[str] = None
    next_position: Optional[int] = None
    messages: List[Event] = field(default_factory=list)
    errors: List[WebAPIErrorInfo] = field(default_factory=list)
    chat_ended: bool = False
    monitored: bool = False
    idle_timer_expire: Optional[int] = None
    user_data: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatOperationResult":
        """Create ChatOperationResult from dictionary."""
        messages = [
            Event.from_dict(msg) for msg in data.get("messages", [])
        ]
        errors = [
            WebAPIErrorInfo.from_dict(err) for err in data.get("errors", [])
        ]

        return cls(
            status_code=data.get("statusCode", 0),
            chat_id=data.get("chatId"),
            secure_key=data.get("secureKey"),
            user_id=data.get("userId"),
            alias=data.get("alias"),
            next_position=data.get("nextPosition"),
            messages=messages,
            errors=errors,
            chat_ended=data.get("chatEnded", False),
            monitored=data.get("monitored", False),
            idle_timer_expire=data.get("idleTimerExpire"),
            user_data=data.get("userData", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ChatOperationResult to dictionary."""
        return {
            "statusCode": self.status_code,
            "chatId": self.chat_id,
            "secureKey": self.secure_key,
            "userId": self.user_id,
            "alias": self.alias,
            "nextPosition": self.next_position,
            "messages": [msg.to_dict() for msg in self.messages],
            "errors": [err.to_dict() for err in self.errors],
            "chatEnded": self.chat_ended,
            "monitored": self.monitored,
            "idleTimerExpire": self.idle_timer_expire,
            "userData": self.user_data,
        }

    @property
    def is_success(self) -> bool:
        """Check if the operation was successful."""
        return self.status_code == 0 and len(self.errors) == 0
