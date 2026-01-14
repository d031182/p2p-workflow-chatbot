# AI Chatbot Assistant Guide

## Overview
The P2P Workflow AI Assistant provides natural language interaction with the procurement system, including advanced root cause analysis for blocked documents.

## Accessing the Chatbot
- **URL:** http://localhost:5000/chatbot
- **Navigation:** Click "🤖 AI Assistant" in the main menu

## Key Capabilities

### 1. Root Cause Analysis for Blocked Documents

When you ask about blocked documents, the chatbot provides:

#### For Purchase Orders:
- **Blocked reason** with context
- **Approval status** - pending/rejected approvers
- **Root cause identification** - vendor compliance, budget issues, etc.
- **Action required** - specific steps to resolve
- **Who to contact** - relevant department/person

#### For Goods Receipts:
- **Blocked reason** with context
- **Root cause analysis** - quantity discrepancies, quality failures, damage
- **Resolution steps** - verify quantities, inspect goods, file claims
- **Contact information** - warehouse manager, vendor, shipping carrier

#### For Invoices (Most Advanced):
- **Blocked reason** with detailed context
- **Three-way matching analysis** - PO vs GR vs Invoice
- **Price variance calculation**:
  - PO amount vs Invoice amount
  - Dollar variance
  - Percentage variance
  - Severity level (HIGH/MEDIUM/LOW)
- **Approval status tracking**:
  - Required approvers based on amount
  - Who has approved
  - Who is pending
- **Tolerance rule violations**
- **Missing authorization detection**
- **Urgency indicators**:
  - Days overdue (if applicable)
  - Payment priority status

### 2. Example Questions

#### Blocked Document Analysis:
- "Show blocked documents"
- "What's blocked?"
- "Analyze blocked invoices"

#### Statistics & Summaries:
- "Show statistics"
- "How many POs do we have?"
- "Total spend"

#### Document Search:
- "Find PO-12345"
- "Show invoice INV-67890"
- "Search for GR-ABCD"

#### Process Explanations:
- "Explain P2P process"
- "How does approval work?"
- "What is three-way matching?"

#### Financial Queries:
- "Show overdue invoices"
- "What's paid?"
- "Payment information"

#### Pending Items:
- "What needs approval?"
- "Show pending approvals"

### 3. Advanced Features

#### Smart Pattern Matching
The chatbot understands natural language variations:
- "blocked docs" = "blocked documents" = "what's stuck"
- "pending" = "waiting" = "needs approval"
- "explain p2p" = "what is p2p" = "how does p2p work"

#### Contextual Analysis
For blocked documents, the chatbot:
1. Identifies the document type
2. Analyzes the block reason
3. Calculates financial impact
4. Determines severity level
5. Provides actionable resolution steps
6. Suggests who to contact

#### Price Variance Analysis Example
```
Invoice INV-12345 blocked due to pricing discrepancy:
• PO Amount: $10,000.00
• Invoice Amount: $11,200.00
• Variance: $1,200.00 (12.0%)
• Severity: HIGH - Variance exceeds 10% tolerance
• Action: Validate invoice line items against PO
• Contact: Accounts Payable and vendor
```

#### Approval Tracking Example
```
Invoice requires approval from:
• John Smith (Dept Manager) ✅ Approved
• Sarah Johnson (Finance Manager) ⏳ Pending
• Michael Brown (CFO) ⏳ Pending
```

### 4. Use Cases

#### Scenario 1: Invoice Blocked - Price Discrepancy
**User:** "Show blocked documents"

**Chatbot Response:**
- Lists all blocked documents
- For each invoice: calculates exact price variance
- Indicates severity level
- Provides resolution steps

#### Scenario 2: Goods Receipt Issues
**User:** "What's blocked?"

**Chatbot Response:**
- Identifies quantity discrepancies
- Points to specific GR issues
- Suggests contacting warehouse manager
- Provides next steps

#### Scenario 3: Missing Approvals
**User:** "Blocked invoices"

**Chatbot Response:**
- Shows which approvers are pending
- Displays approval chain
- Indicates urgency if overdue
- Suggests escalation path

### 5. Response Format

All blocked document responses include:
- 📊 **Analysis section** with root cause
- 💰 **Financial impact** with amounts
- 🚫 **Blocked reason** clearly stated
- ✅ **Action required** - specific steps
- 👥 **Contact information** - who to reach out to
- ⚠️ **Urgency indicators** - if time-sensitive

### 6. Tips for Best Results

1. **Be conversational** - "What's blocked?" works as well as "Show blocked documents"
2. **Use document numbers** - "Find PO-12345" for specific searches
3. **Ask follow-ups** - After seeing blocked docs, ask "Explain P2P process"
4. **Check urgency** - Ask "Overdue invoices" to prioritize
5. **Type 'help'** - Get full list of capabilities anytime

### 7. Technical Details

#### Root Cause Detection Logic:
- **Vendor issues:** Detects "vendor", "compliance" keywords
- **Budget issues:** Identifies budget-related blocks
- **Quantity issues:** Recognizes "quantity", "discrepancy"
- **Quality issues:** Detects "quality", "damage" problems
- **Price issues:** Calculates variance and tolerance
- **Approval issues:** Tracks approval chain status

#### Severity Calculations:
- **HIGH:** >10% price variance, overdue invoices
- **MEDIUM:** 5-10% price variance
- **LOW:** <5% price variance

#### Response Time:
- Instant analysis for all queries
- Real-time data from workflow system
- No external API calls required

## Architecture

The chatbot uses:
- **Rule-based NLP** for pattern matching
- **Workflow integration** for real-time data
- **Context-aware analysis** for blocked documents
- **Mathematical calculations** for variance analysis
- **Policy matching** for approval requirements

## Future Enhancements (Potential)

- Integration with external LLM for more sophisticated NLP
- Predictive analytics for block prevention
- Automated resolution suggestions
- Email/notification integration
- Voice interface support

---

**Built with:** Python, Flask, Rule-based NLP
**Last Updated:** January 2026
