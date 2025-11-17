# Quick Start Guide

## 1. Setup (First Time Only)

```bash
# Copy and edit your config
cp config.example.json data.json
nano data.json  # Edit with your API details

# Make bot executable
chmod +x genesys_bot.py
```

## 2. Quick Commands

### Test Connection
```bash
./genesys_bot.py
```

### Normal Conversation
```bash
./genesys_bot.py -m file -f payloads/normal_conversation.txt
```

### WAF Testing - All Payloads
```bash
./genesys_bot.py -m payload -p all
```

### WAF Testing - XSS Only
```bash
./genesys_bot.py -m payload -p xss
```

### WAF Testing - SQL Injection
```bash
./genesys_bot.py -m payload -p sqli
```

### Interactive Chat
```bash
./genesys_bot.py -m interactive
```

### Custom Payload File
```bash
./genesys_bot.py -m file -f your_payloads.txt
```

## 3. Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `-c FILE` | Config file | `-c myconfig.json` |
| `-m MODE` | Mode (file/payload/interactive/simple) | `-m payload` |
| `-p TYPE` | Payload type | `-p xss` |
| `-f FILE` | Message file | `-f payloads/test.txt` |
| `-d SEC` | Delay between messages | `-d 5` |
| `-v` | Verbose logging | `-v` |
| `--stop-on-block` | Stop if WAF blocks | `--stop-on-block` |

## 4. With Burp Suite

1. Edit `data.json`:
```json
"proxies": {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}
```

2. Start Burp Suite on port 8080
3. Run bot normally - all traffic goes through Burp

## 5. Payload Types

- `xss` - Cross-Site Scripting
- `sqli` - SQL Injection
- `cmdi` - Command Injection
- `path_traversal` - Path Traversal
- `xxe` - XML External Entity
- `normal` - Normal conversation
- `all` - Everything above

## 6. Create Custom Payloads

```bash
cat > my_test.txt << EOF
Hello, normal message
<script>alert(1)</script>
' OR '1'='1
Another normal message
EOF

./genesys_bot.py -m file -f my_test.txt
```

## 7. Troubleshooting

**403 Forbidden:** WAF is blocking you - check Burp Suite logs
**Connection error:** Check proxy settings and URL in config
**No messages:** Chat may have ended - check transcript position
