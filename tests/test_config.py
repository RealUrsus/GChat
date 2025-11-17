"""Unit tests for configuration management."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from genesys_chat.config import ChatConfig


class TestChatConfig(unittest.TestCase):
    """Test ChatConfig class."""

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "url": "https://gms.example.com/genesys/2/chat/TestService/",
            "headers": {"apikey": "test-key-123"},
            "verify": False,
            "proxies": {
                "http": "http://proxy:8080",
                "https": "http://proxy:8080",
            },
            "data": {
                "nickname": "TestUser",
                "firstName": "Test",
                "lastName": "User",
                "emailAddress": "test@example.com",
                "subject": "Test Subject",
                "userData[lang]": "en",
                "userData[source]": "web",
            },
        }

        config = ChatConfig.from_dict(data)

        self.assertEqual(
            config.base_url, "https://gms.example.com/genesys/2/chat/"
        )
        self.assertEqual(config.service_name, "TestService")
        self.assertEqual(config.api_key, "test-key-123")
        self.assertFalse(config.verify_ssl)
        self.assertEqual(config.proxy_http, "http://proxy:8080")
        self.assertEqual(config.nickname, "TestUser")
        self.assertEqual(config.first_name, "Test")
        self.assertEqual(config.email_address, "test@example.com")
        self.assertIn("lang", config.user_data)
        self.assertEqual(config.user_data["lang"], "en")

    def test_from_file(self):
        """Test creating config from JSON file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            config_data = {
                "url": "https://gms.example.com/genesys/2/chat/TestService/",
                "headers": {"apikey": "test-key"},
                "data": {"nickname": "TestUser"},
            }
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = ChatConfig.from_file(temp_path)
            self.assertEqual(config.service_name, "TestService")
            self.assertEqual(config.api_key, "test-key")
        finally:
            os.unlink(temp_path)

    def test_from_file_not_found(self):
        """Test from_file with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            ChatConfig.from_file("/nonexistent/path/config.json")

    def test_from_env(self):
        """Test creating config from environment variables."""
        # Set environment variables
        os.environ["GENESYS_BASE_URL"] = "https://test.example.com/genesys/2/chat/"
        os.environ["GENESYS_SERVICE_NAME"] = "TestService"
        os.environ["GENESYS_API_KEY"] = "env-key-123"
        os.environ["GENESYS_TIMEOUT"] = "60"
        os.environ["GENESYS_VERIFY_SSL"] = "false"
        os.environ["GENESYS_NICKNAME"] = "EnvUser"

        try:
            config = ChatConfig.from_env()

            self.assertEqual(
                config.base_url, "https://test.example.com/genesys/2/chat/"
            )
            self.assertEqual(config.service_name, "TestService")
            self.assertEqual(config.api_key, "env-key-123")
            self.assertEqual(config.timeout, 60)
            self.assertFalse(config.verify_ssl)
            self.assertEqual(config.nickname, "EnvUser")
        finally:
            # Clean up environment variables
            for key in [
                "GENESYS_BASE_URL",
                "GENESYS_SERVICE_NAME",
                "GENESYS_API_KEY",
                "GENESYS_TIMEOUT",
                "GENESYS_VERIFY_SSL",
                "GENESYS_NICKNAME",
            ]:
                os.environ.pop(key, None)

    def test_from_env_missing_vars(self):
        """Test from_env with missing required variables."""
        # Ensure variables are not set
        for key in ["GENESYS_BASE_URL", "GENESYS_SERVICE_NAME", "GENESYS_API_KEY"]:
            os.environ.pop(key, None)

        with self.assertRaises(ValueError) as context:
            ChatConfig.from_env()

        self.assertIn("Missing required environment variables", str(context.exception))

    def test_get_proxies(self):
        """Test get_proxies method."""
        # With proxies
        config1 = ChatConfig(
            base_url="https://test.com/",
            service_name="test",
            api_key="key",
            proxy_http="http://proxy:8080",
            proxy_https="http://proxy:8080",
        )
        proxies = config1.get_proxies()
        self.assertIsNotNone(proxies)
        self.assertEqual(proxies["http"], "http://proxy:8080")
        self.assertEqual(proxies["https"], "http://proxy:8080")

        # Without proxies
        config2 = ChatConfig(
            base_url="https://test.com/", service_name="test", api_key="key"
        )
        self.assertIsNone(config2.get_proxies())

    def test_get_full_url(self):
        """Test get_full_url method."""
        config = ChatConfig(
            base_url="https://gms.example.com/genesys/2/chat/",
            service_name="TestService",
            api_key="key",
        )

        # Without endpoint
        url1 = config.get_full_url()
        self.assertEqual(url1, "https://gms.example.com/genesys/2/chat/TestService/")

        # With endpoint
        url2 = config.get_full_url("refresh")
        self.assertEqual(
            url2, "https://gms.example.com/genesys/2/chat/TestService/refresh"
        )


if __name__ == "__main__":
    unittest.main()
