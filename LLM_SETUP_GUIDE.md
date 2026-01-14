# LLM Integration Setup Guide

## Overview
The P2P Workflow chatbot can be enhanced with OpenAI's GPT models for more sophisticated natural language understanding and conversational responses.

## Benefits of LLM Integration

### Enhanced Capabilities
- **Better Natural Language Understanding**: Understands complex, conversational queries
- **Contextual Responses**: Provides more nuanced, context-aware answers
- **Intelligent Explanations**: Can explain processes in multiple ways based on user needs
- **Follow-up Questions**: Better at handling multi-turn conversations
- **Enhanced Presentation**: Makes structured data more readable and actionable

### Hybrid Approach
The system uses a **hybrid architecture**:
1. **Rule-based system** for queries requiring real-time data (stats, blocked docs, search)
2. **LLM enhancement** to make responses more conversational and helpful
3. **LLM processing** for general questions about processes and workflows
4. **Automatic fallback** to rule-based if LLM is unavailable

## Setup Instructions

### Option 1: Using OpenAI API (Recommended)

#### Step 1: Get OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

#### Step 2: Install OpenAI Package
```bash
pip install openai
```

#### Step 3: Set Environment Variable

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-key-here
```

**Permanent (Add to .env file):**
```
OPENAI_API_KEY=sk-your-key-here
```

#### Step 4: Update web_app.py
Replace the chatbot initialization:

```python
# Change this line:
from chatbot import P2PChatbot
chatbot = P2PChatbot(workflow)

# To this:
from chatbot_llm import P2PChatbotLLM
chatbot = P2PChatbotLLM(workflow)
```

#### Step 5: Restart the Application
```bash
python web_app.py
```

You should see: `✓ LLM integration enabled (OpenAI GPT)`

### Option 2: Using Azure OpenAI

If your organization uses Azure OpenAI:

```python
import openai

openai.api_type = "azure"
openai.api_base = "https://YOUR-ENDPOINT.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "YOUR-AZURE-KEY"
```

### Option 3: Using Local LLM (Advanced)

For privacy-sensitive environments, you can use local LLMs:

1. **Ollama** (https://ollama.ai/)
2. **LocalAI** (https://github.com/go-skynet/LocalAI)
3. **LM Studio** (https://lmstudio.ai/)

Modify `chatbot_llm.py` to use local endpoint instead of OpenAI API.

## Configuration Options

### Model Selection

In `chatbot_llm.py`, you can choose different models:

```python
# For general queries (faster, cheaper)
model="gpt-3.5-turbo"

# For complex analysis (better quality)
model="gpt-4"

# For enhanced responses
model="gpt-3.5-turbo"  # Balances cost and quality
```

### Cost Optimization

**Estimated Costs** (as of 2024):
- GPT-3.5-turbo: ~$0.002 per chat interaction
- GPT-4: ~$0.03 per chat interaction

**Tips to reduce costs:**
1. Use GPT-3.5-turbo for most queries
2. Only use GPT-4 for complex analysis
3. Cache common responses
4. Set reasonable `max_tokens` limits
5. Use rule-based system for structured data queries

### Temperature Settings

Adjust in `_process_with_llm()`:

```python
temperature=0.3  # More focused, deterministic (0.0-1.0)
temperature=0.7  # Balanced (default)
temperature=0.9  # More creative, varied responses
```

## Testing LLM Integration

### Without API Key (Rule-based mode):
```
User: "What is P2P?"
Response: Rule-based explanation with structured format
```

### With API Key (LLM-enhanced mode):
```
User: "What is P2P?"
Response: Conversational, context-aware explanation with examples from your actual data
```

### Hybrid Mode (Best of both):
```
User: "Show blocked documents"
Response: 
1. Rule-based system fetches real-time data
2. LLM enhances presentation and adds insights
3. Result: Structured data + conversational analysis
```

## Example Queries

### General Questions (Uses LLM):
- "Can you explain the approval process in simple terms?"
- "What's the best way to handle a vendor dispute?"
- "How do I prioritize overdue invoices?"
- "What are common reasons for blocked documents?"

### Data Queries (Uses Rule-based + LLM Enhancement):
- "Show me blocked documents" → Real data + LLM analysis
- "What's pending?" → Real stats + LLM insights
- "Find PO-12345" → Exact data + LLM context

## Troubleshooting

### Issue: "No API key found"
**Solution:** Set `OPENAI_API_KEY` environment variable

### Issue: "OpenAI package not installed"
**Solution:** Run `pip install openai`

### Issue: "Rate limit exceeded"
**Solution:** 
- Wait a moment and try again
- Upgrade OpenAI plan
- Use caching for common queries

### Issue: "Model not found"
**Solution:** Check model name and API access level

### Issue: "Connection timeout"
**Solution:**
- Check internet connection
- Verify API endpoint
- System will fallback to rule-based mode

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or secret management
3. **Rotate keys** regularly
4. **Monitor usage** through OpenAI dashboard
5. **Set spending limits** in OpenAI account
6. **Use least-privilege access** (read-only if possible)

## Monitoring & Analytics

### Check LLM Usage:
- OpenAI Dashboard: https://platform.openai.com/usage
- Monitor token consumption
- Track costs per day/month
- Analyze query patterns

### Performance Metrics:
- Response time (typically 1-3 seconds)
- Token usage per query
- Fallback frequency
- User satisfaction

## Alternative LLM Providers

### Anthropic Claude
```python
import anthropic
client = anthropic.Client(api_key=API_KEY)
```

### Google PaLM
```python
import google.generativeai as palm
palm.configure(api_key=API_KEY)
```

### Cohere
```python
import cohere
co = cohere.Client(API_KEY)
```

## Benefits Summary

| Feature | Rule-based | LLM-Enhanced | Hybrid (Recommended) |
|---------|-----------|--------------|----------------------|
| Real-time data | ✅ | ❌ | ✅ |
| Natural language | ⚠️ Limited | ✅ | ✅ |
| Cost | Free | $$$ | $$ |
| Response quality | Good | Excellent | Excellent |
| Offline capable | ✅ | ❌ | ⚠️ Partial |
| Conversational | ⚠️ Limited | ✅ | ✅ |
| Consistency | ✅ | ⚠️ Varies | ✅ |

## Getting Started

**Quick Start** (No API key needed):
- Current setup works perfectly with rule-based system
- Provides all functionality with structured responses

**Enhanced Experience** (With API key):
- More natural conversations
- Better explanations
- Context-aware insights
- Improved user experience

**Recommendation**: Start with rule-based (free), then add LLM when you want enhanced conversational capabilities.

---

**Questions?** The chatbot works great in both modes! The LLM integration is optional but provides a more natural conversation experience.
