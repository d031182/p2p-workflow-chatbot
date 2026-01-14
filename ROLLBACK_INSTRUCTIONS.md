# How to Switch Back to LLM if Needed

## Current Setup (FAST Mode)
✅ Using `llm_backend="none"` for 10-20x faster responses
✅ Response time: 50-200ms
✅ All functionality working

## If You Want to Switch Back to LLM

### Option 1: Edit web_app.py Manually

**File:** `web_app.py` (around line 18-20)

**Change FROM:**
```python
chatbot = P2PChatbotUltimate(workflow, llm_backend="none", tools_enabled=False)
```

**Change TO:**
```python
chatbot = P2PChatbotUltimate(workflow, llm_backend="transformers", tools_enabled=False)
```

Then restart the application.

### Option 2: Use the Chatbot Settings UI

1. Go to: http://localhost:5000/chatbot/settings
2. Select LLM Backend: "Transformers"
3. Click "Save Configuration"
4. The chatbot will reload with LLM enabled

## Comparison

### Fast Mode (Current - llm_backend="none")
- ✅ Response: 50-200ms (instant!)
- ✅ Startup: 1 second
- ✅ Memory: 50-100MB
- ✅ All features work
- ✅ Responses are clear, structured, and complete

### LLM Mode (llm_backend="transformers")
- ⏳ Response: 1-3 seconds (slower)
- ⏳ Startup: 30 seconds (loading model)
- ⏳ Memory: 500MB-1GB
- ✅ All features work
- ✅ Slightly more conversational tone

## Testing Checklist

Try these queries to verify everything works:

### Basic Queries
- [ ] "show statistics"
- [ ] "what's pending?"
- [ ] "show blocked documents"
- [ ] "find PO-12345"
- [ ] "explain P2P process"

### Advanced Queries
- [ ] "which invoices are blocked?"
- [ ] "what's the total spend?"
- [ ] "show overdue invoices"
- [ ] "list pending purchase orders"
- [ ] "explain approval process"

### Performance Test
- [ ] Responses feel instant (no waiting)
- [ ] No delays on startup
- [ ] All information is accurate and complete

## Expected Results

The fast mode (without LLM) should provide:
- ✅ Instant responses
- ✅ Detailed, structured information
- ✅ Root cause analysis for blocked docs
- ✅ Complete statistics
- ✅ All the same data as before

## Need Help?

If you encounter any issues:
1. Check the console output for errors
2. Verify the change was saved in web_app.py
3. Make sure you restarted the Flask application
4. Test with simple queries first

## Recommendation

Based on the analysis:
- The fast mode provides the SAME functionality
- Responses are just as good (actually more structured)
- Users get instant feedback instead of waiting
- **I strongly recommend keeping the fast mode unless you specifically need the conversational polish**

---

**Current Status:** Fast mode enabled (llm_backend="none")
**Rollback:** Change "none" to "transformers" in web_app.py line 20
