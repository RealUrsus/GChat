"""Configuration management for Genesys Chat client."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import json


@dataclass
class ChatConfig:
    """Configuration for Genesys Chat client."""

    # API Configuration
    base_url: str
    service_name: str
    api_key: str

    # Request Configuration
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True

    # Proxy Configuration
    proxy_http: Optional[str] = None
    proxy_https: Optional[str] = None

    # User Information
    nickname: str = "Guest"
    first_name: str = ""
    last_name: str = ""
    email_address: str = ""
    subject: str = ""

    # User Data
    user_data: Dict[str, str] = field(default_factory=dict)

    # HTTP Headers
    custom_headers: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_file(cls, file_path: str) -> "ChatConfig":
        """Load configuration from JSON file.

        Args:
            file_path: Path to configuration file

        Returns:
            ChatConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatConfig":
        """Create configuration from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            ChatConfig instance
        """
        # Extract base URL and service name
        url = data.get("url", "")
        # Parse URL to extract base and service name
        # Example: "https://gms.example.com/genesys/2/chat/CE18_Digital_Chat/"
        parts = url.rstrip("/").split("/")
        service_name = parts[-1] if parts else ""
        base_url = "/".join(parts[:-1]) + "/" if parts else url

        # Extract proxy configuration
        proxies = data.get("proxies", {})
        proxy_http = proxies.get("http")
        proxy_https = proxies.get("https")

        # Extract headers
        headers = data.get("headers", {})
        api_key = headers.get("apikey", "")

        # Extract user data
        form_data = data.get("data", {})
        user_data = {}
        for key, value in form_data.items():
            if key.startswith("userData["):
                # Extract key name from userData[key]
                user_data_key = key[9:-1]
                user_data[user_data_key] = value

        return cls(
            base_url=base_url,
            service_name=service_name,
            api_key=api_key,
            verify_ssl=data.get("verify", True),
            proxy_http=proxy_http,
            proxy_https=proxy_https,
            nickname=form_data.get("nickname", "Guest"),
            first_name=form_data.get("firstName", ""),
            last_name=form_data.get("lastName", ""),
            email_address=form_data.get("emailAddress", ""),
            subject=form_data.get("subject", ""),
            user_data=user_data,
            custom_headers=headers,
        )

    @classmethod
    def from_env(cls) -> "ChatConfig":
        """Load configuration from environment variables.

        Returns:
            ChatConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        required_vars = ["GENESYS_BASE_URL", "GENESYS_SERVICE_NAME", "GENESYS_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return cls(
            base_url=os.getenv("GENESYS_BASE_URL", ""),
            service_name=os.getenv("GENESYS_SERVICE_NAME", ""),
            api_key=os.getenv("GENESYS_API_KEY", ""),
            timeout=int(os.getenv("GENESYS_TIMEOUT", "30")),
            max_retries=int(os.getenv("GENESYS_MAX_RETRIES", "3")),
            verify_ssl=os.getenv("GENESYS_VERIFY_SSL", "true").lower() == "true",
            proxy_http=os.getenv("HTTP_PROXY"),
            proxy_https=os.getenv("HTTPS_PROXY"),
            nickname=os.getenv("GENESYS_NICKNAME", "Guest"),
            first_name=os.getenv("GENESYS_FIRST_NAME", ""),
            last_name=os.getenv("GENESYS_LAST_NAME", ""),
            email_address=os.getenv("GENESYS_EMAIL", ""),
            subject=os.getenv("GENESYS_SUBJECT", ""),
        )

    def get_proxies(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration.

        Returns:
            Proxy dictionary or None if no proxies configured
        """
        proxies = {}
        if self.proxy_http:
            proxies["http"] = self.proxy_http
        if self.proxy_https:
            proxies["https"] = self.proxy_https

        return proxies if proxies else None

    def get_full_url(self, endpoint: str = "") -> str:
        """Get full URL for an endpoint.

        Args:
            endpoint: API endpoint (e.g., 'refresh', 'send')

        Returns:
            Full URL
        """
        if endpoint:
            return f"{self.base_url}{self.service_name}/{endpoint}"
        return f"{self.base_url}{self.service_name}/"
