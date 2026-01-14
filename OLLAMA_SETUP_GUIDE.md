# Ollama Setup Guide - 100% Free LLM Integration

## Why Ollama?

✅ **Completely FREE** - No API costs, ever
✅ **Runs Locally** - No internet required after download
✅ **Private** - Your data never leaves your computer
✅ **No API Keys** - No registration or limits
✅ **Unlimited Usage** - Use as much as you want
✅ **Multiple Models** - Llama2, Mistral, Codellama, and more

## Quick Start (5 Minutes)

### Step 1: Download Ollama
Visit: **https://ollama.ai/download**

- Windows: Download and run installer
- Mac: Download .dmg file
- Linux: Run `curl -fsSL https://ollama.ai/install.sh | sh`

### Step 2: Install a Model
After installation, open a terminal and run:

```bash
ollama pull llama2
```

This downloads the Llama2 model (~4GB). Other options:
- `ollama pull mistral` - Faster, efficient
- `ollama pull codellama` - Best for code
- `ollama pull llama2:13b` - Larger, better quality

### Step 3: Verify Ollama is Running

```bash
ollama list
```

You should see your installed models.

### Step 4: Update Your Web App

Edit `web_app.py` and change:

```python
# FROM:
from chatbot import P2PChatbot
chatbot = P2PChatbot(workflow)

# TO:
from chatbot_ollama import P2PChatbotOllama
chatbot = P2PChatbotOllama(workflow)
```

### Step 5: Restart Application

```bash
python web_app.py
```

You should see: `✓ Ollama integration enabled (Model: llama2)`

## Available Models

### Recommended for P2P Chatbot:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama2** | 4GB | Medium | Good | General purpose (recommended) |
| **mistral** | 4GB | Fast | Good | Quick responses |
| **llama2:13b** | 7GB | Slower | Better | Complex analysis |
| **codellama** | 4GB | Medium | Good | Technical queries |

### Switch Models:

```python
# In web_app.py:
chatbot = P2PChatbotOllama(workflow, model="mistral")
```

## How It Works

### Hybrid Architecture:
1. **Data Queries** (blocked, stats, search) → Rule-based gets real data
2. **LLM Enhancement** → Ollama makes responses more conversational
3. **General Questions** → Pure Ollama for explanations
4. **Automatic Fallback** → Rule-based if Ollama unavailable

### Example Flow:

**User:** "Which invoices are blocked?"

1. Rule-based system fetches blocked invoices
2. Ollama enhances the presentation
3. Result: Accurate data + conversational response

## System Requirements

### Minimum:
- 8GB RAM
- 10GB free disk space
- Modern CPU (any from last 5 years)

### Recommended:
- 16GB RAM for better performance
- SSD for faster model loading
- GPU optional (CPU works fine)

## Testing Ollama

### Check if Running:
```bash
curl http://localhost:11434/api/tags
```

### Test Ollama Directly:
```bash
ollama run llama2
```

Type a question, like: "What is P2P?"

### Exit:
Type `/bye`

## Comparison: Rule-Based vs Ollama

| Feature | Rule-Based | With Ollama |
|---------|-----------|-------------|
| Cost | Free | Free |
| Speed | Instant | 1-3 seconds |
| Accuracy | Perfect for data | Perfect for data |
| Conversational | Limited | Excellent |
| Privacy | ✅ | ✅ |
| Offline | ✅ | ✅ (after download) |
| Setup Time | 0 min | 5 min |

## Troubleshooting

### Issue: "Ollama not available"
**Solution:**
1. Check if Ollama is running: `ollama list`
2. If not installed, download from https://ollama.ai
3. Pull a model: `ollama pull llama2`
4. Ollama runs automatically after installation

### Issue: "Connection refused"
**Solution:**
- Ollama service may not be running
- Restart Ollama or your computer
- Check: `curl http://localhost:11434`

### Issue: "Model not found"
**Solution:**
```bash
ollama pull llama2
```

### Issue: Slow responses
**Solution:**
- Use faster model: `mistral`
- Close other applications
- First response is slower (model loads)
- Subsequent responses are faster

## Advanced Configuration

### Change Model in Code:

```python
# Faster responses
chatbot = P2PChatbotOllama(workflow, model="mistral")

# Better quality
chatbot = P2PChatbotOllama(workflow, model="llama2:13b")

# Best for code
chatbot = P2PChatbotOllama(workflow, model="codellama")
```

### Adjust Response Style:

In `chatbot_ollama.py`, modify:

```python
"options": {
    "temperature": 0.3,  # More focused (0.0-1.0)
    "top_p": 0.9         # Creativity control
}
```

## Free LLM Alternatives

If you can't use Ollama:

1. **LM Studio** - https://lmstudio.ai/
   - GUI interface
   - Same local models
   - Windows/Mac friendly

2. **GPT4All** - https://gpt4all.io/
   - Simple installer
   - Multiple models
   - Easy to use

3. **Hugging Face** - Free API tier
   - Cloud-based
   - Limited free usage
   - Internet required

## Why Ollama is Best for P2P:

✅ **Privacy** - Sensitive procurement data stays local
✅ **Cost** - Zero ongoing costs
✅ **Performance** - Fast on modern hardware
✅ **Reliability** - No API rate limits
✅ **Hybrid Approach** - Best of rule-based + LLM

## Recommendation

**Start with:** Rule-based (current setup) - works great!
**Upgrade to:** Ollama if you want more conversational responses
**Consider:** OpenAI/Azure for enterprise deployment

The rule-based chatbot is already excellent for structured queries. Ollama adds natural conversation without any costs!

---

**Installation Time:** 5 minutes
**Cost:** $0 forever
**Privacy:** 100% local
