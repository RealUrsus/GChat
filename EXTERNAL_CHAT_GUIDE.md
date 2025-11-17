# External Chat Service Guide

This guide explains how to use the external chat service feature to create semi-mindful conversations that emulate actual web chat interactions.

## Overview

The GChat bot now supports three conversation modes:

1. **File Mode** - Traditional mode using local text files
2. **External Mode** - Fully AI-driven conversations using external chat services
3. **Hybrid Mode** - Combines file-based prompts with AI-generated responses

## Features

- **Semi-Mindful Conversations**: AI services maintain context and generate natural responses
- **Multiple Providers**: Support for OpenAI, Groq, Together AI, and custom endpoints
- **Flexible Integration**: Works seamlessly with existing Genesys chat testing
- **Easy Configuration**: CLI arguments or environment variables

## Supported Services

### 1. Groq (Recommended - Free & Fast)

Groq offers free, fast inference for open-source models.

**Setup:**
1. Get API key from: https://console.groq.com/keys
2. Set environment variable: `export EXTERNAL_API_KEY=your_groq_key`

**Usage:**
```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key YOUR_GENESYS_KEY \
  -m external \
  --external-service groq \
  --external-api-key YOUR_GROQ_KEY \
  --max-turns 10
```

**Available Models:**
- `llama-3.1-8b-instant` (default, fast)
- `llama-3.1-70b-versatile` (more capable)
- `mixtral-8x7b-32768` (large context)

### 2. OpenAI

**Setup:**
1. Get API key from: https://platform.openai.com/api-keys
2. Set environment variable: `export EXTERNAL_API_KEY=your_openai_key`

**Usage:**
```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key YOUR_GENESYS_KEY \
  -m external \
  --external-service openai \
  --external-model gpt-3.5-turbo \
  --max-turns 10
```

**Available Models:**
- `gpt-3.5-turbo` (default, cost-effective)
- `gpt-4` (more capable, higher cost)
- `gpt-4-turbo` (balanced)

### 3. Together AI

**Setup:**
1. Get API key from: https://api.together.xyz/settings/api-keys
2. Set environment variable: `export EXTERNAL_API_KEY=your_together_key`

**Usage:**
```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key YOUR_GENESYS_KEY \
  -m external \
  --external-service together \
  --external-model meta-llama/Llama-3-8b-chat-hf
```

### 4. Custom OpenAI-Compatible Endpoint

For self-hosted or other OpenAI-compatible services.

**Usage:**
```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key YOUR_GENESYS_KEY \
  -m external \
  --external-service custom \
  --external-base-url https://your-api.example.com/v1 \
  --external-model your-model-name
```

## Operation Modes

### External Mode

Generates fully AI-driven conversations with configurable turn limits.

**Example:**
```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m external \
  --external-service groq \
  --max-turns 20 \
  --delay 3
```

**What it does:**
1. Starts both Genesys and external chat sessions
2. Sends initial prompts to external AI
3. Gets AI responses and sends them to Genesys
4. Continues conversation for max-turns iterations
5. Maintains context throughout the conversation

### Hybrid Mode

Uses prompts from a local file but gets AI responses, creating more realistic conversations.

**Example:**
```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m hybrid \
  -f payloads/normal_conversation.txt \
  --external-service groq
```

**What it does:**
1. Reads user prompts from local file
2. For each prompt, gets AI response
3. Sends both prompt and response to Genesys
4. Creates realistic back-and-forth conversation

**File Format:**
```
Hello, I need help with my account
Can you help me reset my password?
What are your business hours?
Thank you for your help!
```

## Configuration Options

### CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--external-service` | Provider (openai/groq/together/custom) | Required for external/hybrid |
| `--external-api-key` | API key for external service | Can use EXTERNAL_API_KEY env var |
| `--external-base-url` | Base URL for custom service | N/A |
| `--external-model` | Model name | Provider-specific defaults |
| `--external-system-prompt` | System prompt for AI | "You are a helpful customer service assistant..." |
| `--max-turns` | Maximum conversation turns | 10 |
| `-d, --delay` | Delay between messages (seconds) | 2 |

### Environment Variables

Add to `.env` file:

```bash
# External chat service API key
EXTERNAL_API_KEY=your_api_key_here
```

### Custom System Prompts

Customize the AI's behavior:

```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m external \
  --external-service groq \
  --external-system-prompt "You are an angry customer complaining about a product defect. Be persistent but professional."
```

## Use Cases

### 1. WAF Testing with Natural Conversations

Test WAF with realistic conversation patterns:

```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m hybrid \
  -f payloads/normal_conversation.txt \
  --external-service groq
```

### 2. Load Testing with Variable Content

Generate unique conversations for each test run:

```bash
for i in {1..10}; do
  python genesys_bot.py \
    -s gms.example.com \
    --service MyService \
    --api-key GENESYS_KEY \
    -m external \
    --external-service groq \
    --max-turns 15 &
done
```

### 3. Conversation Flow Testing

Test how the system handles natural conversation flows:

```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m external \
  --external-service groq \
  --external-system-prompt "You are a customer asking about product features. Ask follow-up questions based on responses." \
  --max-turns 20
```

### 4. Semi-Mindful Security Testing

Create contextual security payloads:

```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m hybrid \
  -f payloads/xss_advanced.txt \
  --external-service groq
```

## Architecture

### New Components

1. **chat_services.py** - Abstract base class for chat services
   - `BaseChatService`: Interface for all chat services
   - `ChatMessage`: Message data structure
   - `ChatResponse`: Response data structure

2. **external_chat_service.py** - External service implementations
   - `ExternalChatService`: Generic OpenAI-compatible service
   - `GroqChatService`: Groq-specific implementation
   - `OpenAIChatService`: OpenAI-specific implementation
   - `TogetherAIChatService`: Together AI implementation

3. **conversation_sources.py** - Conversation source abstractions
   - `FileConversationSource`: Load from local files
   - `ExternalServiceConversationSource`: Generate with AI
   - `HybridConversationSource`: Combine file + AI

### Integration Flow

```
User Input (CLI)
    ↓
Create External Chat Service (if needed)
    ↓
Initialize Genesys Client
    ↓
Start Genesys Session
    ↓
Create Conversation Source
    ↓
For each message from source:
    ├── Get message (from file or AI)
    ├── Send to Genesys
    └── Refresh Genesys (get responses)
    ↓
End sessions (Genesys + External)
```

## Best Practices

1. **Start with Groq**: Free tier, fast responses, good for testing
2. **Use Hybrid Mode**: More realistic than pure external or file-based
3. **Customize System Prompts**: Tailor AI behavior to test scenarios
4. **Monitor Costs**: Track API usage for paid services
5. **Test Incrementally**: Start with low max-turns, increase gradually

## Troubleshooting

### "API key not configured"

**Solution**: Set API key via CLI or environment variable:
```bash
export EXTERNAL_API_KEY=your_key
# or
--external-api-key your_key
```

### "Request timeout"

**Solution**: Increase timeout in service config or use faster model:
```bash
--external-model llama-3.1-8b-instant  # Faster than 70b
```

### "Model not found"

**Solution**: Check provider's documentation for available models:
- Groq: https://console.groq.com/docs/models
- OpenAI: https://platform.openai.com/docs/models
- Together: https://docs.together.ai/docs/inference-models

## Examples

### Example 1: Quick Test with Groq

```bash
# Set API key
export EXTERNAL_API_KEY=gsk_...

# Run external conversation
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m external \
  --external-service groq \
  --max-turns 5
```

### Example 2: Hybrid with Custom Prompts

```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m hybrid \
  -f payloads/normal_conversation.txt \
  --external-service groq \
  --external-system-prompt "You are a helpful customer service agent. Provide detailed, friendly responses."
```

### Example 3: Long Conversation with OpenAI

```bash
python genesys_bot.py \
  -s gms.example.com \
  --service MyService \
  --api-key GENESYS_KEY \
  -m external \
  --external-service openai \
  --external-model gpt-3.5-turbo \
  --max-turns 30 \
  --delay 2
```

## API Rate Limits

| Provider | Free Tier | Rate Limit |
|----------|-----------|------------|
| Groq | Yes | 30 requests/minute |
| OpenAI | Trial credits | Varies by tier |
| Together AI | $25 free | Varies by model |

## Next Steps

1. Get API key from your preferred provider
2. Test with external mode (5-10 turns)
3. Try hybrid mode with existing payload files
4. Customize system prompts for specific scenarios
5. Integrate into automated testing workflows

## Support

For issues or questions:
- Check the main README.md for general setup
- Review API provider documentation for service-specific issues
- File issues at project repository
