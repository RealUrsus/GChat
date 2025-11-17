# Genesys Web Chat Testing Bot

A powerful testing tool for WAF and Genesys Web Chat v2 API security testing and conversation generation.

## Features

- ✅ **Complete Genesys Chat v2 API Support** - All endpoints properly implemented
- 🛡️ **WAF Testing** - Built-in payloads for XSS, SQLi, Command Injection, Path Traversal, XXE
- 🤖 **Conversation Bot** - Automated conversation generation and testing
- 📝 **Multiple Modes** - File-based, payload testing, interactive, and simple modes
- 🌐 **NEW: External Chat Services** - Integration with OpenAI, Groq, Together AI for semi-mindful conversations
- 🔀 **NEW: Hybrid Mode** - Combine file prompts with AI-generated responses for realistic chats
- 🎯 **Payload Generators** - Pre-built payload sets with encoding variants
- 📊 **Better Logging** - Clear, structured logging with request tracking
- ⚙️ **Flexible Configuration** - Command-line based configuration (no config files needed!)

## Improvements Over Original

### Code Quality
- **Better Structure**: Separated concerns into classes (Client, Bot, PayloadGenerator)
- **Type Hints**: Added type annotations for better code clarity
- **PEP 8 Compliant**: Clean, readable Python code style
- **Better Naming**: snake_case for functions, descriptive variable names
- **Error Handling**: Proper exception handling without sys.exit() everywhere
- **No Config Files**: All configuration via CLI arguments and environment variables

### Features
- **6 Operation Modes**: Simple, File, Payload, Interactive, External, Hybrid
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

### .env File (Recommended)

Create a `.env` file in the project directory:

```bash
# Copy example file
cp .env.example .env

# Edit with your values
GENESYS_SERVER=gms.example.com
GENESYS_SERVICE=MyServiceName
GENESYS_API_KEY=your_api_key_here
```

### Environment Variables

```bash
# Required
export GENESYS_SERVER=gms.example.com
export GENESYS_SERVICE=MyServiceName
export GENESYS_API_KEY=your_api_key_here

# Optional
export HTTP_PROXY=http://127.0.0.1:8080
export HTTPS_PROXY=http://127.0.0.1:8080
```

### Command-Line Arguments

**Required (if not in .env):**
- `-s, --server` - Server hostname (e.g., gms.example.com)
- `--service` - Service name (e.g., MyServiceName)
- `--api-key` - API key

**Optional:**
- `--use-http` - Use HTTP instead of HTTPS (default: HTTPS)
- `--nickname` - User nickname (default: TestUser)
- `--first-name` - First name (default: Test)
- `--last-name` - Last name (default: User)
- `--email` - Email address (default: test@example.com)
- `--subject` - Chat subject (default: Testing)
- `--proxy-http` - HTTP proxy URL
- `--proxy-https` - HTTPS proxy URL
- `--verify-ssl` - Enable SSL verification (disabled by default)

**Note:** The path `/genesys/2/chat/{ServiceName}/` is built automatically. HTTPS is used by default.

## Usage

### 1. Simple Mode (Quick Test)

Send a single test message:

```bash
# Using .env file (recommended)
python genesys_bot.py -s gms.example.com --service MyService

# Using environment variables
export GENESYS_SERVER=gms.example.com
export GENESYS_SERVICE=MyService
export GENESYS_API_KEY=your_api_key
python genesys_bot.py

# Or pass everything via CLI
python genesys_bot.py -s gms.example.com --service MyService --api-key YOUR_KEY

# With custom initial message
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_KEY \
    --initial-message "Test message"
```

### 2. File Mode (Conversation from File)

Send messages from a text file (one message per line):

```bash
# Using .env file
python genesys_bot.py -m file -f payloads/normal_conversation.txt

# With custom delay between messages
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_KEY \
    -m file -f payloads/waf_test_basic.txt -d 3
```

### 3. Payload Testing Mode (WAF Testing)

Test specific payload types:

```bash
# Test all payload types (using .env file)
python genesys_bot.py -m payload -p all

# Test only XSS payloads
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_KEY \
    -m payload -p xss

# Test SQL injection with 5-second delays
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_KEY \
    -m payload -p sqli -d 5

# Stop on first WAF block
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_KEY \
    -m payload -p all --stop-on-block
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
# Using .env file
python genesys_bot.py -m interactive

# Or with CLI args
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_KEY \
    -m interactive
```

Commands in interactive mode:
- `/refresh` - Refresh and show new messages
- `/quit` - Disconnect and exit

### 5. External Mode (AI-Driven Conversations) 🆕

Use external AI chat services to generate realistic, semi-mindful conversations:

```bash
# Using Groq (free, fast)
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_GENESYS_KEY \
    -m external \
    --external-service groq \
    --external-api-key YOUR_GROQ_KEY \
    --max-turns 10

# Using OpenAI
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_GENESYS_KEY \
    -m external \
    --external-service openai \
    --external-model gpt-3.5-turbo \
    --max-turns 15

# With custom system prompt
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_GENESYS_KEY \
    -m external \
    --external-service groq \
    --external-system-prompt "You are an angry customer complaining about service."
```

**Supported Services:**
- `groq` - Groq (free, fast, recommended)
- `openai` - OpenAI
- `together` - Together AI
- `custom` - Custom OpenAI-compatible endpoint

### 6. Hybrid Mode (File Prompts + AI Responses) 🆕

Combine file-based prompts with AI-generated responses for the most realistic conversations:

```bash
# Using file prompts with AI responses
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_GENESYS_KEY \
    -m hybrid \
    -f payloads/normal_conversation.txt \
    --external-service groq \
    --external-api-key YOUR_GROQ_KEY

# Or use environment variable
export EXTERNAL_API_KEY=your_groq_key
python genesys_bot.py -s gms.example.com --service MyService \
    --api-key YOUR_GENESYS_KEY \
    -m hybrid \
    -f payloads/normal_conversation.txt \
    --external-service groq
```

**📖 For detailed external service setup and usage, see [EXTERNAL_CHAT_GUIDE.md](EXTERNAL_CHAT_GUIDE.md)**

### Advanced Options

```bash
# Enable verbose debug logging
python genesys_bot.py -v -m payload -p xss

# Use with Burp Suite proxy
python genesys_bot.py -s gms.example.com --service MyService \
    --proxy-http http://127.0.0.1:8080 \
    --proxy-https http://127.0.0.1:8080 \
    -m payload -p xss

# Add initial delay before starting chat
python genesys_bot.py -s gms.example.com --service MyService \
    --initial-delay 5 -m payload -p sqli

# Custom user information
python genesys_bot.py -s gms.example.com --service MyService \
    --nickname "SecurityTester" \
    --first-name "John" \
    --last-name "Doe" \
    --email "john@example.com" \
    -m interactive

# Use HTTP instead of HTTPS (if needed)
python genesys_bot.py -s gms.example.com --service MyService \
    --use-http \
    -m simple
```

## Example Workflows

### 1. WAF Bypass Testing

```bash
# Create .env file with credentials
cat > .env << 'EOF'
GENESYS_SERVER=target.com
GENESYS_SERVICE=MyServiceName
GENESYS_API_KEY=your_api_key
HTTP_PROXY=http://127.0.0.1:8080
HTTPS_PROXY=http://127.0.0.1:8080
EOF

# Test with Burp Suite proxy
python genesys_bot.py -m payload -p xss -d 2 -v

# Monitor Burp Suite for:
# - Which payloads get through
# - Which get blocked
# - Response differences
```

### 2. Conversation Simulation

```bash
# Create realistic conversation flow (using .env)
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

# Test with .env configured
python genesys_bot.py -m file -f custom_payloads.txt
```

## File Structure

```
GChat/
├── genesys_bot.py              # Main bot script (refactored & improved)
├── .env                        # Your configuration (create from .env.example)
├── .env.example                # Example configuration file
├── README.md                   # This file
├── QUICK_START.md              # Quick start guide
├── IMPROVEMENTS.md             # Detailed improvements documentation
├── payloads/                   # Payload files
│   ├── waf_test_basic.txt     # Basic WAF tests
│   ├── xss_advanced.txt       # Advanced XSS payloads
│   ├── sqli_advanced.txt      # Advanced SQL injection
│   └── normal_conversation.txt # Normal chat messages
└── genesys_chat/               # Modular library
    ├── __init__.py
    ├── client.py              # Full-featured client
    ├── models.py              # Type-safe data models
    ├── logger.py              # Logging utilities
    └── exceptions.py          # Custom exceptions
```

## Code Improvements Summary

### Original Code Issues → Solutions

| Issue | Original | Improved |
|-------|----------|----------|
| **Config files** | JSON files with secrets | .env + CLI args + env vars |
| **Hardcoded URLs** | Full URLs in config | Just hostname, path auto-built |
| **Protocol** | Hardcoded in URL | HTTPS by default, --use-http flag |
| **Mixed concerns** | Everything in one class | Separated: Client, Bot, PayloadGenerator |
| **Poor naming** | `printData`, `gms_dict` | `_log_message`, `ChatSession` |
| **No type safety** | No type hints | Full type annotations |
| **Magic values** | Hardcoded strings | Constants and clear defaults |
| **sys.exit()** | Called everywhere | Proper returns and exceptions |
| **print() logging** | Mixed print statements | Structured logging |

### Key Refactorings

1. **No Config Files Needed - Use .env Instead**
   ```bash
   # Before: Create and edit JSON files
   cp config.example.json data.json
   vim data.json  # Edit full URL, API key, etc.
   python genesys_bot.py -c data.json

   # After: Use .env file (recommended)
   cp .env.example .env
   vim .env  # Just hostname, service name, API key
   python genesys_bot.py

   # Or environment variables
   export GENESYS_SERVER=gms.example.com
   export GENESYS_SERVICE=MyService
   export GENESYS_API_KEY=your_key
   python genesys_bot.py

   # Or CLI (for quick tests)
   python genesys_bot.py -s gms.example.com --service MyService --api-key KEY
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

1. **Use Environment Variables**: Keep API keys secure with `GENESYS_API_KEY`
2. **Use Burp Suite**: Configure proxy with `--proxy-http` and `--proxy-https`
3. **Start Normal**: Begin with normal conversation to establish baseline
4. **Gradual Testing**: Test payload categories one at a time
5. **Monitor Responses**: Check for different response patterns
6. **Encoding Tests**: Use encoding variants for bypass attempts
7. **Rate Limiting**: Add delays to avoid triggering rate limits
8. **Mix Traffic**: Combine normal and malicious traffic patterns

## Quick Start

```bash
# 1. Install dependencies (optional: python-dotenv for .env support)
pip install requests urllib3 python-dotenv

# 2. Create .env file
cp .env.example .env
# Edit .env with your server, service name, and API key

# 3. Run a simple test
python genesys_bot.py

# 4. Test with payloads
python genesys_bot.py -m payload -p xss

# 5. Interactive mode
python genesys_bot.py -m interactive
```

## Troubleshooting

**Missing configuration error:**
- Create `.env` file from `.env.example`, or
- Set environment variables: `GENESYS_SERVER`, `GENESYS_SERVICE`, `GENESYS_API_KEY`, or
- Pass via CLI: `-s hostname --service ServiceName --api-key KEY`

**Chat won't start:**
- Verify server hostname (just `gms.example.com`, not full URL)
- Check service name is correct
- Check API key is valid
- Try with `--verify-ssl` if SSL issues occur
- Use `-v` for verbose logging to see the constructed URL

**WAF blocking everything:**
- Try normal conversation first with `-m payload -p normal`
- Increase delays between messages with `-d 5`
- Check if proxy is interfering

**No messages received:**
- Check transcript position in logs
- Try `/refresh` in interactive mode
- Verify chat session is still active

**python-dotenv not installed:**
- Install with `pip install python-dotenv`, or
- Use environment variables or CLI arguments instead

## License

MIT License - Use for authorized security testing only.

## Disclaimer

This tool is intended for authorized security testing and educational purposes only. Always obtain proper authorization before testing any system you don't own.
