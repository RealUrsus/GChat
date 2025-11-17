"""Genesys Web Chat v2 API client implementation."""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import ChatConfig
from .exceptions import (
    GenesysChatAPIError,
    GenesysChatConnectionError,
    GenesysChatTimeoutError,
)
from .models import ChatOperationResult, Event, EventType

logger = logging.getLogger(__name__)


class GenesysChatClient:
    """Client for interacting with Genesys Web Chat v2 API.

    This client provides a comprehensive interface to all Genesys Web Chat v2
    API endpoints with proper error handling, logging, and type safety.

    Example:
        >>> config = ChatConfig.from_file("config.json")
        >>> client = GenesysChatClient(config)
        >>> result = client.start_chat("Hello from chatbot!")
        >>> print(f"Chat ID: {result.chat_id}")
    """

    def __init__(self, config: ChatConfig):
        """Initialize the Genesys Chat client.

        Args:
            config: Configuration for the client
        """
        self.config = config
        self._session = self._create_session()
        self._chat_id: Optional[str] = None
        self._secure_key: Optional[str] = None
        self._user_id: Optional[str] = None
        self._alias: Optional[str] = None
        self._transcript_position: int = 0

    def _create_session(self) -> requests.Session:
        """Create and configure HTTP session with retry logic.

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(
            {
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded",
                "apikey": self.config.api_key,
                **self.config.custom_headers,
            }
        )

        return session

    def _make_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> ChatOperationResult:
        """Make HTTP request to the API.

        Args:
            endpoint: API endpoint (e.g., 'refresh', 'send')
            data: Form data to send
            files: Files to upload

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatConnectionError: If connection fails
            GenesysChatAPIError: If API returns an error
            GenesysChatTimeoutError: If request times out
        """
        url = self._get_chat_url(endpoint)

        logger.debug(f"Making request to {url}")
        logger.debug(f"Data: {data}")

        try:
            proxies = self.config.get_proxies()

            if files:
                # For file uploads, use multipart/form-data
                response = self._session.post(
                    url,
                    data=data,
                    files=files,
                    proxies=proxies,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl,
                )
            else:
                response = self._session.post(
                    url,
                    data=data,
                    proxies=proxies,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl,
                )

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")

            response.raise_for_status()

            # Parse JSON response
            json_data = response.json()
            result = ChatOperationResult.from_dict(json_data)

            # Check for API-level errors
            if not result.is_success:
                error_messages = [
                    f"{err.code}: {err.message}" for err in result.errors
                ]
                raise GenesysChatAPIError(
                    f"API returned errors: {', '.join(error_messages)}",
                    status_code=result.status_code,
                    errors=[err.to_dict() for err in result.errors],
                )

            return result

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise GenesysChatTimeoutError(f"Request timed out: {e}") from e

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise GenesysChatConnectionError(f"Connection failed: {e}") from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise GenesysChatConnectionError(f"Request failed: {e}") from e

    def _get_chat_url(self, endpoint: str = "") -> str:
        """Get full URL for chat endpoint.

        Args:
            endpoint: Endpoint name

        Returns:
            Full URL
        """
        if self._chat_id and endpoint:
            return f"{self.config.base_url}{self.config.service_name}/{self._chat_id}/{endpoint}"
        elif self._chat_id:
            return f"{self.config.base_url}{self.config.service_name}/{self._chat_id}"
        else:
            return self.config.get_full_url(endpoint)

    def _prepare_common_data(
        self, additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare common form data for requests.

        Args:
            additional_data: Additional data to include

        Returns:
            Form data dictionary
        """
        data = {
            "alias": self._alias or "",
            "secureKey": self._secure_key or "",
            "userId": self._user_id or "",
            "transcriptPosition": self._transcript_position,
        }

        if additional_data:
            data.update(additional_data)

        return data

    # ========================================================================
    # Chat Session Management
    # ========================================================================

    def start_chat(
        self,
        initial_message: str = "",
        **kwargs: Any,
    ) -> ChatOperationResult:
        """Start a new chat session.

        Args:
            initial_message: Initial message to send
            **kwargs: Additional parameters (firstName, lastName, etc.)

        Returns:
            ChatOperationResult with chat session details

        Raises:
            GenesysChatAPIError: If chat creation fails
        """
        logger.info("Starting new chat session")

        data = {
            "nickname": self.config.nickname,
            "firstName": self.config.first_name,
            "lastName": self.config.last_name,
            "emailAddress": self.config.email_address,
            "subject": self.config.subject,
            "text": initial_message,
        }

        # Add user data
        for key, value in self.config.user_data.items():
            data[f"userData[{key}]"] = value

        # Add any additional kwargs
        data.update(kwargs)

        result = self._make_request("", data)

        # Store session details
        self._chat_id = result.chat_id
        self._secure_key = result.secure_key
        self._user_id = result.user_id
        self._alias = result.alias
        self._transcript_position = result.next_position or 0

        logger.info(f"Chat started successfully. Chat ID: {self._chat_id}")

        return result

    def refresh(self, position: Optional[int] = None) -> ChatOperationResult:
        """Refresh chat to get new messages and events.

        Args:
            position: Transcript position to refresh from.
                      0 = no events, 1 = all events, None = current position

        Returns:
            ChatOperationResult with new messages

        Raises:
            GenesysChatAPIError: If refresh fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        if position is not None:
            self._transcript_position = position

        logger.debug(
            f"Refreshing chat from position {self._transcript_position}"
        )

        data = self._prepare_common_data()
        result = self._make_request("refresh", data)

        # Update transcript position
        if result.next_position is not None:
            self._transcript_position = result.next_position

        logger.debug(f"Refresh returned {len(result.messages)} messages")

        return result

    def disconnect(self) -> ChatOperationResult:
        """Disconnect from chat session.

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If disconnect fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Disconnecting from chat {self._chat_id}")

        data = self._prepare_common_data()
        result = self._make_request("disconnect", data)

        # Clear session details
        self._chat_id = None
        self._secure_key = None
        self._user_id = None
        self._alias = None
        self._transcript_position = 0

        logger.info("Disconnected successfully")

        return result

    # ========================================================================
    # Messaging
    # ========================================================================

    def send_message(self, message: str) -> ChatOperationResult:
        """Send a message in the chat.

        Args:
            message: Message text to send

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If message send fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Sending message: {message}")

        data = self._prepare_common_data({"message": message})
        result = self._make_request("send", data)

        # Update transcript position
        if result.next_position is not None:
            self._transcript_position = result.next_position

        return result

    def send_custom_notice(
        self, message: str, message_type: str = "notice"
    ) -> ChatOperationResult:
        """Send a custom notification.

        Args:
            message: Notification message
            message_type: Type of notification

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If send fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Sending custom notice: {message}")

        data = self._prepare_common_data(
            {"message": message, "messageType": message_type}
        )
        result = self._make_request("customNotice", data)

        if result.next_position is not None:
            self._transcript_position = result.next_position

        return result

    # ========================================================================
    # Typing Indicators
    # ========================================================================

    def start_typing(self) -> ChatOperationResult:
        """Send typing started indicator.

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If request fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.debug("Sending typing started indicator")

        data = self._prepare_common_data()
        return self._make_request("startTyping", data)

    def stop_typing(self) -> ChatOperationResult:
        """Send typing stopped indicator.

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If request fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.debug("Sending typing stopped indicator")

        data = self._prepare_common_data()
        return self._make_request("stopTyping", data)

    # ========================================================================
    # File Operations
    # ========================================================================

    def upload_file(
        self, file_path: str, message: Optional[str] = None
    ) -> ChatOperationResult:
        """Upload a file to the chat.

        Args:
            file_path: Path to file to upload
            message: Optional message to send with file

        Returns:
            ChatOperationResult

        Raises:
            FileNotFoundError: If file doesn't exist
            GenesysChatAPIError: If upload fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Uploading file: {file_path}")

        data = self._prepare_common_data()
        if message:
            data["message"] = message

        with open(path, "rb") as f:
            files = {"file": (path.name, f, "application/octet-stream")}
            result = self._make_request("file", data, files)

        if result.next_position is not None:
            self._transcript_position = result.next_position

        logger.info("File uploaded successfully")

        return result

    def check_file_limits(self) -> ChatOperationResult:
        """Check file upload limits and constraints.

        Returns:
            ChatOperationResult with file limit information

        Raises:
            GenesysChatAPIError: If request fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.debug("Checking file upload limits")

        data = self._prepare_common_data()
        return self._make_request("file/limits", data)

    def delete_file(self, file_id: str) -> ChatOperationResult:
        """Delete a previously uploaded file.

        Args:
            file_id: ID of the file to delete

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If deletion fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Deleting file: {file_id}")

        data = self._prepare_common_data()
        result = self._make_request(f"file/{file_id}/delete", data)

        logger.info("File deleted successfully")

        return result

    def download_file(self, file_id: str, save_path: str) -> None:
        """Download a file from the chat.

        Args:
            file_id: ID of the file to download
            save_path: Path where to save the downloaded file

        Raises:
            GenesysChatAPIError: If download fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Downloading file {file_id} to {save_path}")

        url = self._get_chat_url(f"file/{file_id}/download")
        data = self._prepare_common_data()

        try:
            response = self._session.post(
                url,
                data=data,
                proxies=self.config.get_proxies(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                stream=True,
            )

            response.raise_for_status()

            # Save file
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info("File downloaded successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"File download failed: {e}")
            raise GenesysChatConnectionError(f"File download failed: {e}") from e

    # ========================================================================
    # User Data Management
    # ========================================================================

    def update_nickname(self, nickname: str) -> ChatOperationResult:
        """Update user's nickname.

        Args:
            nickname: New nickname

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If update fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Updating nickname to: {nickname}")

        data = self._prepare_common_data({"nickname": nickname})
        return self._make_request("updateNickname", data)

    def update_user_data(self, user_data: Dict[str, str]) -> ChatOperationResult:
        """Update user data.

        Args:
            user_data: Dictionary of user data to update

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If update fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Updating user data: {user_data}")

        data = self._prepare_common_data()

        # Add user data with proper formatting
        for key, value in user_data.items():
            data[f"userData[{key}]"] = value

        return self._make_request("updateData", data)

    # ========================================================================
    # Advanced Features
    # ========================================================================

    def set_push_url(self, push_url: str) -> ChatOperationResult:
        """Set or update push URL for notifications.

        Args:
            push_url: URL for push notifications

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If request fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.info(f"Setting push URL: {push_url}")

        data = self._prepare_common_data({"pushUrl": push_url})
        return self._make_request("pushUrl", data)

    def send_read_receipt(self, transcript_position: int) -> ChatOperationResult:
        """Send read receipt for a specific message.

        Args:
            transcript_position: Position of the message that was read

        Returns:
            ChatOperationResult

        Raises:
            GenesysChatAPIError: If request fails
        """
        if not self._chat_id:
            raise GenesysChatAPIError("No active chat session")

        logger.debug(f"Sending read receipt for position {transcript_position}")

        data = self._prepare_common_data()
        data["transcriptPosition"] = transcript_position

        return self._make_request("readReceipt", data)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def get_messages(
        self, event_type: Optional[EventType] = None
    ) -> List[Event]:
        """Get messages from the last refresh.

        Args:
            event_type: Filter by specific event type (e.g., EventType.MESSAGE)

        Returns:
            List of events
        """
        result = self.refresh()

        if event_type:
            return [msg for msg in result.messages if msg.type == event_type]

        return result.messages

    def wait_for_message(
        self,
        timeout: int = 60,
        poll_interval: int = 2,
        event_type: EventType = EventType.MESSAGE,
    ) -> Optional[Event]:
        """Wait for a specific type of message.

        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: How often to poll for messages
            event_type: Type of event to wait for

        Returns:
            The first matching event or None if timeout

        Raises:
            GenesysChatTimeoutError: If timeout is reached
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            messages = self.get_messages(event_type)

            if messages:
                return messages[0]

            time.sleep(poll_interval)

        raise GenesysChatTimeoutError(
            f"Timeout waiting for {event_type.value} message"
        )

    @property
    def chat_id(self) -> Optional[str]:
        """Get current chat ID."""
        return self._chat_id

    @property
    def is_active(self) -> bool:
        """Check if chat session is active."""
        return self._chat_id is not None

    def __enter__(self) -> "GenesysChatClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - disconnect if active."""
        if self.is_active:
            try:
                self.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
