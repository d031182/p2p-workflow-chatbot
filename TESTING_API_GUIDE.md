# Testing API Guide

## Overview

The `test_chatbot_api.py` provides a programmatic way to test the P2P Chatbot without needing to use the browser. This is especially useful for:

- **Automated testing** after code changes
- **Verifying features** like KG reasoning, tools, and analytics
- **Quick iteration** during development
- **Regression testing** to ensure changes don't break existing functionality

## Installation

No additional dependencies needed! The script uses the standard `requests` library which is already in `requirements.txt`.

## Usage

### 1. Basic Usage - Run All Tests

```bash
python test_chatbot_api.py
```

This runs all test suites:
- Basic chatbot queries (statistics, help, etc.)
- Knowledge Graph reasoning tests
- Analytical tools tests

### 2. Test Knowledge Graph Reasoning Only

```bash
python test_chatbot_api.py kg
```

This specifically tests the KG reasoning functionality:
- Finds blocked documents in the system
- Asks "why" questions about specific blocked documents
- Verifies that HTML visualizations are returned
- Checks for proper KG reasoning analysis

**Expected Output:**
```
🧠 Testing Knowledge Graph Reasoning
============================================================

1. Finding blocked documents...
Response: ...

   Found blocked invoice: INV-XXXXXXXX

2. Testing KG reasoning queries...

============================================================
Test 1/3: why is invoice INV-XXXXXXXX blocked?
============================================================
✅ Response received (2570 chars)
📊 HTML visualization detected
   → Blocked document analysis

✅ Knowledge Graph Reasoning is working!
```

### 3. Test Analytical Tools Only

```bash
python test_chatbot_api.py tools
```

Tests all analytical tools:
- Outlier detection (invoices, POs)
- Spending trends (by vendor, department, month)
- Statistical analysis

**Expected Output:**
```
🔧 Testing Analytical Tools
============================================================

Test 1/5: find outliers in invoices
============================================================
✅ Response received (3500+ chars)
📊 HTML visualization detected
   → Outlier analysis

✅ Tools are working! (5/5 returned visualizations)
```

### 4. Interactive Mode

```bash
python test_chatbot_api.py interactive
```

Provides a command-line interface to chat with the bot:

```
💬 Interactive Testing Mode
============================================================
Type 'exit' or 'quit' to stop

You: why is invoice INV-1BB4F2E2 blocked?

📊 HTML Response (2570 chars)
   (View in browser at http://localhost:5000/chatbot)
   🔴 HIGH severity detected
   🟡 MEDIUM severity detected

You: show statistics
