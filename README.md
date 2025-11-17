# Genesys Web Chat Testing Bot

A powerful testing tool for WAF and Genesys Web Chat v2 API security testing and conversation generation.

## Features

- ✅ **Complete Genesys Chat v2 API Support** - All endpoints properly implemented
- 🛡️ **WAF Testing** - Built-in payloads for XSS, SQLi, Command Injection, Path Traversal, XXE
- 🤖 **Conversation Bot** - Automated conversation generation and testing
- 📝 **Multiple Modes** - File-based, payload testing, interactive, and simple modes
- 🎯 **Payload Generators** - Pre-built payload sets with encoding variants
- 📊 **Better Logging** - Clear, structured logging with request tracking
- ⚙️ **Flexible Configuration** - JSON-based configuration with proxy support

## Improvements Over Original

### Code Quality
- **Better Structure**: Separated concerns into classes (Client, Bot, PayloadGenerator)
- **Type Hints**: Added type annotations for better code clarity
- **PEP 8 Compliant**: Clean, readable Python code style
- **Better Naming**: snake_case for functions, descriptive variable names
- **Error Handling**: Proper exception handling without sys.exit() everywhere

### Features
- **4 Operation Modes**: Simple, File, Payload, Interactive
- **WAF Detection**: Automatically detects and logs WAF blocks
- **Request Counter**: Tracks total requests made
- **Flexible Delays**: Configurable delays for realistic conversation timing
- **Payload Categories**: Organized payload types (XSS, SQLi, etc.)
- **Better Logging**: Timestamp-based logging with emoji indicators

### Security Testing
- **Multiple Attack Vectors**: XSS, SQLi, CMDi, Path Traversal, XXE
- **Encoding Variants**: Automatic payload encoding for WAF bypass
- **Normal Traffic**: Ability to mix normal and malicious traffic
- **Stop on Block**: Optional flag to stop when WAF blocks

## Installation

```bash
# Clone or download the repository
cd GChat

# Install dependencies
pip install requests urllib3

# Make the bot executable
chmod +x genesys_bot.py
```

## Configuration

1. Copy the example configuration:
```bash
cp config.example.json data.json
```

2. Edit `data.json` with your details:
   - Update `url` with your Genesys Chat endpoint
   - Set your `apikey` in headers
   - Configure proxy settings if needed (Burp Suite, etc.)
   - Customize user data fields

## Usage

### 1. Simple Mode (Quick Test)

Send a single test message:

```bash
python genesys_bot.py
# or
python genesys_bot.py -m simple --initial-message "Test message"
```

### 2. File Mode (Conversation from File)

Send messages from a text file (one message per line):

```bash
python genesys_bot.py -m file -f payloads/normal_conversation.txt

# With custom delay between messages
python genesys_bot.py -m file -f payloads/waf_test_basic.txt -d 3
```

### 3. Payload Testing Mode (WAF Testing)

Test specific payload types:

```bash
# Test all payload types
python genesys_bot.py -m payload -p all

# Test only XSS payloads
python genesys_bot.py -m payload -p xss

# Test SQL injection with 5-second delays
python genesys_bot.py -m payload -p sqli -d 5

# Stop on first WAF block
python genesys_bot.py -m payload -p all --stop-on-block
```

Available payload types:
- `xss` - Cross-Site Scripting
- `sqli` - SQL Injection
- `cmdi` - Command Injection
- `path_traversal` - Path Traversal
- `xxe` - XML External Entity
- `normal` - Normal conversation
- `all` - All of the above

### 4. Interactive Mode (Manual Testing)

Interactive chat session with manual message input:

```bash
python genesys_bot.py -m interactive
```

Commands in interactive mode:
- `/refresh` - Refresh and show new messages
- `/quit` - Disconnect and exit

### Advanced Options

```bash
# Enable verbose debug logging
python genesys_bot.py -v -m payload -p xss

# Use custom config file
python genesys_bot.py -c myconfig.json -m file -f messages.txt

# Add initial delay before starting chat
python genesys_bot.py --initial-delay 5 -m payload -p sqli

# Custom initial message when starting chat
python genesys_bot.py --initial-message "Hello agent!" -m interactive
```

## Example Workflows

### 1. WAF Bypass Testing

```bash
# Test with Burp Suite proxy
# 1. Configure proxy in data.json
# 2. Run payload tests
python genesys_bot.py -m payload -p xss -d 2 -v

# Monitor Burp Suite for:
# - Which payloads get through
# - Which get blocked
# - Response differences
```

### 2. Conversation Simulation

```bash
# Create realistic conversation flow
python genesys_bot.py -m file -f payloads/normal_conversation.txt -d 3

# Mix normal and malicious traffic
cat payloads/normal_conversation.txt payloads/xss_advanced.txt > mixed.txt
python genesys_bot.py -m file -f mixed.txt -d 2
```

### 3. Custom Payload Testing

```bash
# Create your own payload file
cat > custom_payloads.txt << 'EOF'
Normal message 1
<svg/onload=alert(1)>
Normal message 2
' OR 1=1--
Normal message 3
EOF

python genesys_bot.py -m file -f custom_payloads.txt
```

## File Structure

```
GChat/
├── genesys_bot.py              # Main bot script (refactored & improved)
├── gchat.py                    # Original script (kept for reference)
├── data.json                   # Your configuration file
├── config.example.json         # Example configuration
├── README.md                   # This file
├── payloads/                   # Payload files
│   ├── waf_test_basic.txt     # Basic WAF tests
│   ├── xss_advanced.txt       # Advanced XSS payloads
│   ├── sqli_advanced.txt      # Advanced SQL injection
│   └── normal_conversation.txt # Normal chat messages
└── genesys_chat/               # Modular library (optional)
    ├── __init__.py
    ├── client.py              # Full-featured client
    ├── models.py              # Type-safe data models
    ├── config.py              # Configuration management
    └── exceptions.py          # Custom exceptions
```

## Code Improvements Summary

### Original Code Issues → Solutions

| Issue | Original | Improved |
|-------|----------|----------|
| **Mixed concerns** | Everything in one class | Separated: Client, Bot, PayloadGenerator |
| **Poor naming** | `printData`, `gms_dict` | `_log_message`, `ChatSession` |
| **No type safety** | No type hints | Full type annotations |
| **Magic values** | Hardcoded strings | Constants and enums |
| **sys.exit()** | Called everywhere | Proper returns and exceptions |
| **print() logging** | Mixed print statements | Structured logging |
| **No organization** | Single 220-line file | Clean modular code |
| **Limited features** | 4 endpoints | 15+ endpoints + helpers |

### Key Refactorings

1. **Class-Based Design**
   ```python
   # Before: Functions with global state
   def commit(self, output:str = None) -> json:
       # Complex logic

   # After: Clean methods with clear responsibility
   def _make_request(self, url: str, data: Dict[str, Any], description: str = "") -> Optional[Dict[str, Any]]:
       """Make HTTP request to Genesys API."""
   ```

2. **Better Data Management**
   ```python
   # Before: Dictionary soup
   self.gms_dict["chatId"] = json_data["chatId"]
   self.gms_dict["secureKey"] = json_data["secureKey"]

   # After: Structured dataclass
   @dataclass
   class ChatSession:
       chat_id: str
       secure_key: str
       user_id: str
       alias: str
       transcript_position: int
   ```

3. **Proper Logging**
   ```python
   # Before:
   print("(+) Got Chat ID")

   # After:
   logger.info("✅ Chat started successfully")
   logger.info(f"   Chat ID: {self.session.chat_id}")
   ```

## OpenAPI Compliance

The refactored client implements all endpoints from the OpenAPI specification:

✅ **Chat Management**
- POST `/2/chat/{serviceName}` - Create chat
- POST `/2/chat/{serviceName}/{chatId}/refresh` - Refresh chat
- POST `/2/chat/{serviceName}/{chatId}/disconnect` - Disconnect

✅ **Messaging**
- POST `/2/chat/{serviceName}/{chatId}/send` - Send message
- POST `/2/chat/{serviceName}/{chatId}/customNotice` - Custom notice

✅ **Typing Indicators**
- POST `/2/chat/{serviceName}/{chatId}/startTyping` - Start typing
- POST `/2/chat/{serviceName}/{chatId}/stopTyping` - Stop typing

✅ **File Operations**
- POST `/2/chat/{serviceName}/{chatId}/file` - Upload file
- POST `/2/chat/{serviceName}/{chatId}/file/limits` - Check limits
- POST `/2/chat/{serviceName}/{chatId}/file/{fileId}/delete` - Delete file
- POST `/2/chat/{serviceName}/{chatId}/file/{fileId}/download` - Download file

✅ **User Data**
- POST `/2/chat/{serviceName}/{chatId}/updateNickname` - Update nickname
- POST `/2/chat/{serviceName}/{chatId}/updateData` - Update user data

✅ **Advanced**
- POST `/2/chat/{serviceName}/{chatId}/pushUrl` - Set push URL
- POST `/2/chat/{serviceName}/{chatId}/readReceipt` - Read receipt

## Tips for WAF Testing

1. **Use Burp Suite**: Configure proxy in `data.json` to intercept all traffic
2. **Start Normal**: Begin with normal conversation to establish baseline
3. **Gradual Testing**: Test payload categories one at a time
4. **Monitor Responses**: Check for different response patterns
5. **Encoding Tests**: Use encoding variants for bypass attempts
6. **Rate Limiting**: Add delays to avoid triggering rate limits
7. **Mix Traffic**: Combine normal and malicious traffic patterns

## Troubleshooting

**Chat won't start:**
- Check API key in config
- Verify URL endpoint is correct
- Check proxy settings if using Burp Suite

**WAF blocking everything:**
- Try normal conversation first
- Increase delays between messages
- Check User-Agent string
- Verify SSL verification settings

**No messages received:**
- Check transcript position
- Try `/refresh` in interactive mode
- Verify chat session is still active

## License

MIT License - Use for authorized security testing only.

## Disclaimer

This tool is intended for authorized security testing and educational purposes only. Always obtain proper authorization before testing any system you don't own.
