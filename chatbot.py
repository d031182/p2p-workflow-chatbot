"""
Natural language chatbot for P2P workflow system
Provides conversational interface to query and interact with the workflow
"""
import re
from datetime import datetime


class P2PChatbot:
    def __init__(self, workflow):
        self.workflow = workflow
        
    def process_message(self, user_message: str) -> dict:
        """
        Process user message and return appropriate response
        Returns dict with 'message' and optional 'data' for structured display
        """
        message = user_message.lower().strip()
        
        # Approval policies query - check FIRST
        if ('approval polic' in message or 'approval rule' in message):
            return self._explain_approval_process()
        
        # Which/what queries - handle FIRST before anything else
        if ('which' in message or 'what' in message):
            # Check for blocked queries
            if 'blocked' in message:
                if 'invoice' in message:
                    return self._get_blocked_invoices_only()
                elif 'po' in message or 'purchase order' in message:
                    return self._get_blocked_pos_only()
                elif 'gr' in message or 'goods receipt' in message:
                    return self._get_blocked_grs_only()
                else:
                    return self._get_blocked_documents()
            # Check for pending queries (but not if asking ABOUT policies)
            elif ('pending' in message or 'approval' in message) and 'polic' not in message:
                if 'invoice' in message:
                    return self._get_pending_invoices_only()
                elif 'po' in message or 'purchase order' in message:
                    return self._get_pending_pos_only()
            # Check for overdue
            elif 'overdue' in message:
                return self._get_overdue_info()
        
        # Greeting patterns - only match if it's JUST a greeting
        if message in ['hello', 'hi', 'hey', 'greetings', 'hello!', 'hi!', 'hey!']:
            return {
                'message': "Hello! I'm your P2P Workflow Assistant. I can help you with:\n\n" +
                          "• View statistics and summaries\n" +
                          "• Check pending approvals\n" +
                          "• Find purchase orders, goods receipts, or invoices\n" +
                          "• Explain the P2P process\n" +
                          "• Check blocked documents\n\n" +
                          "Just ask me anything about the procurement process!"
            }
        
        # Help patterns
        if self._matches(message, ['help', 'what can you do', 'commands']):
            return {
                'message': "I can help you with:\n\n" +
                          "📊 **Statistics**: 'show stats', 'how many POs', 'total spend'\n" +
                          "⏳ **Pending**: 'pending approvals', 'what needs approval'\n" +
                          "🚫 **Blocked**: 'blocked documents', 'show blocked items'\n" +
                          "📋 **Search**: 'find PO [number]', 'show invoice [number]'\n" +
                          "❓ **Process**: 'explain P2P', 'how does approval work'\n" +
                          "💰 **Financial**: 'total spend', 'paid invoices', 'overdue'\n\n" +
                          "Try asking in natural language!"
            }
        
        # Statistics queries
        if self._matches(message, ['stats', 'statistics', 'summary', 'overview']):
            return self._get_statistics()
        
        if self._matches(message, ['how many', 'count']) and 'po' in message:
            return self._count_documents('purchase orders')
        
        if self._matches(message, ['how many', 'count']) and ('gr' in message or 'goods receipt' in message):
            return self._count_documents('goods receipts')
        
        if self._matches(message, ['how many', 'count']) and 'invoice' in message:
            return self._count_documents('invoices')
        
        if self._matches(message, ['total spend', 'how much spent', 'spending']):
            return self._get_spend_info()
        
        # Pending approvals (only if not already handled by which/what)
        if self._matches(message, ['pending', 'waiting', 'needs approval', 'awaiting']) and 'which' not in message and 'what' not in message:
            return self._get_pending_approvals()
        
        # Blocked documents - enhanced queries
        if self._matches(message, ['blocked', 'stuck', 'issues', 'problems']):
            # Check if asking about specific document type
            if 'invoice' in message:
                return self._get_blocked_invoices_only()
            elif 'po' in message or 'purchase order' in message:
                return self._get_blocked_pos_only()
            elif 'gr' in message or 'goods receipt' in message:
                return self._get_blocked_grs_only()
            else:
                return self._get_blocked_documents()
        
        # Process explanations
        if self._matches(message, ['explain', 'what is', 'how does']) and 'p2p' in message:
            return self._explain_p2p_process()
        
        if self._matches(message, ['approval', 'approval process', 'how approval']):
            return self._explain_approval_process()
        
        if self._matches(message, ['three-way', '3-way', 'matching']):
            return self._explain_three_way_matching()
        
        # "Why" questions about specific documents
        if self._matches(message, ['why', 'reason']):
            return self._handle_why_question(message)
        
        # Document search
        if self._matches(message, ['find', 'show', 'get', 'search', 'look up']):
            return self._search_documents(message)
        
        # Financial queries
        if self._matches(message, ['paid', 'payments']):
            return self._get_payment_info()
        
        if self._matches(message, ['overdue', 'late', 'past due']):
            return self._get_overdue_info()
        
        # Vendor queries
        if self._matches(message, ['vendor', 'supplier']) and ('list' in message or 'show' in message):
            return self._list_vendors()
        
        # Default response
        return {
            'message': "I'm not sure I understand. Try asking:\n\n" +
                      "• 'Show statistics'\n" +
                      "• 'What's pending approval?'\n" +
                      "• 'Explain the P2P process'\n" +
                      "• 'Find PO [number]'\n" +
                      "• 'Show blocked documents'\n\n" +
                      "Type 'help' for more options!"
        }
    
    def _matches(self, message: str, patterns: list) -> bool:
        """Check if message matches any pattern"""
        return any(pattern in message for pattern in patterns)
    
    def _get_statistics(self) -> dict:
        """Get workflow statistics"""
        stats = self.workflow.get_statistics()
        
        response = f"📊 **Workflow Statistics**\n\n"
        response += f"**Purchase Orders:** {stats['total_pos']}\n"
        response += f"  • Approved: {stats['approved_pos']}\n"
        response += f"  • Pending: {stats['pending_pos']}\n"
        response += f"  • Blocked: {stats['blocked_pos']}\n\n"
        
        response += f"**Goods Receipts:** {stats['total_grs']}\n"
        response += f"  • Accepted: {stats['accepted_grs']}\n"
        response += f"  • Blocked: {stats['blocked_grs']}\n\n"
        
        response += f"**Invoices:** {stats['total_invoices']}\n"
        response += f"  • Paid: {stats['paid_invoices']}\n"
        response += f"  • Overdue: {stats['overdue_invoices']}\n"
        response += f"  • Blocked: {stats['blocked_invoices']}\n\n"
        
        response += f"**💰 Total Spend:** ${stats['total_spend']:,.2f}"
        
        return {'message': response, 'stats': stats}
    
    def _count_documents(self, doc_type: str) -> dict:
        """Count specific document type"""
        if doc_type == 'purchase orders':
            count = len(self.workflow.purchase_orders)
            return {'message': f"There are **{count} purchase orders** in the system."}
        elif doc_type == 'goods receipts':
            count = len(self.workflow.goods_receipts)
            return {'message': f"There are **{count} goods receipts** in the system."}
        elif doc_type == 'invoices':
            count = len(self.workflow.invoices)
            return {'message': f"There are **{count} invoices** in the system."}
    
    def _get_spend_info(self) -> dict:
        """Get spending information"""
        stats = self.workflow.get_statistics()
        return {
            'message': f"💰 **Total Spend (Paid Invoices):** ${stats['total_spend']:,.2f}\n\n" +
                      f"This represents {stats['paid_invoices']} paid invoices."
        }
    
    def _get_pending_approvals(self) -> dict:
        """Get pending approvals"""
        pending = self.workflow.get_all_pending_approvals()
        po_count = len(pending['purchase_orders'])
        inv_count = len(pending['invoices'])
        
        response = f"⏳ **Pending Approvals**\n\n"
        response += f"**Purchase Orders:** {po_count} waiting for approval\n"
        response += f"**Invoices:** {inv_count} waiting for approval\n\n"
        
        if po_count > 0:
            response += "📋 **Recent Pending POs:**\n"
            for po in pending['purchase_orders'][:3]:
                response += f"• {po.po_number} - {po.vendor_name} - ${po.total_amount:,.2f}\n"
        
        if inv_count > 0:
            response += "\n🧾 **Recent Pending Invoices:**\n"
            for inv in pending['invoices'][:3]:
                response += f"• {inv.invoice_number} - {inv.vendor_name} - ${inv.total_amount:,.2f}\n"
        
        if po_count == 0 and inv_count == 0:
            response += "✅ Great! No documents pending approval."
        
        return {'message': response, 'pending': pending}
    
    def _get_blocked_documents(self) -> dict:
        """Get blocked documents with root cause analysis"""
        blocked = self.workflow.get_blocked_documents()
        po_count = len(blocked['purchase_orders'])
        gr_count = len(blocked['goods_receipts'])
        inv_count = len(blocked['invoices'])
        
        total = po_count + gr_count + inv_count
        
        response = f"🚫 **Blocked Documents Analysis**\n\n"
        response += f"**Total Blocked:** {total} documents\n"
        response += f"• Purchase Orders: {po_count}\n"
        response += f"• Goods Receipts: {gr_count}\n"
        response += f"• Invoices: {inv_count}\n\n"
        
        if total == 0:
            response += "✅ No blocked documents. System running smoothly!"
        else:
            response += "⚠️ **Root Cause Analysis:**\n\n"
            
            # Analyze Purchase Orders
            if po_count > 0:
                response += "**Purchase Orders:**\n"
                for po in blocked['purchase_orders']:
                    response += f"• **{po.po_number}** - {po.vendor_name}\n"
                    response += f"  💰 Amount: ${po.total_amount:,.2f}\n"
                    response += f"  🚫 Blocked Reason: {po.blocked_reason}\n"
                    response += self._analyze_po_block(po)
                    response += "\n"
            
            # Analyze Goods Receipts
            if gr_count > 0:
                response += "**Goods Receipts:**\n"
                for gr in blocked['goods_receipts']:
                    response += f"• **{gr.gr_number}** (PO: {gr.po_number})\n"
                    response += f"  💰 Amount: ${gr.total_amount:,.2f}\n"
                    response += f"  🚫 Blocked Reason: {gr.blocked_reason}\n"
                    response += self._analyze_gr_block(gr)
                    response += "\n"
            
            # Analyze Invoices
            if inv_count > 0:
                response += "**Invoices:**\n"
                for inv in blocked['invoices']:
                    response += f"• **{inv.invoice_number}** - {inv.vendor_name}\n"
                    response += f"  💰 Amount: ${inv.total_amount:,.2f}\n"
                    response += f"  🚫 Blocked Reason: {inv.blocked_reason}\n"
                    response += self._analyze_invoice_block(inv)
                    response += "\n"
        
        return {'message': response, 'blocked': blocked}
    
    def _analyze_po_block(self, po) -> str:
        """Analyze root cause of PO block"""
        analysis = "  📊 **Analysis:**\n"
        
        # Check approval status
        if po.approvals:
            pending_approvers = [a.approver for a in po.approvals if a.status == "Pending"]
            rejected_approvers = [a.approver for a in po.approvals if a.status == "Rejected"]
            
            if pending_approvers:
                analysis += f"  • Pending approval from: {', '.join(pending_approvers)}\n"
            if rejected_approvers:
                analysis += f"  • Rejected by: {', '.join(rejected_approvers)}\n"
        
        # Check common block reasons
        if "vendor" in po.blocked_reason.lower():
            analysis += "  • **Action Required:** Verify vendor compliance status\n"
            analysis += "  • **Contact:** Procurement team for vendor validation\n"
        elif "compliance" in po.blocked_reason.lower():
            analysis += "  • **Action Required:** Complete compliance review\n"
            analysis += "  • **Contact:** Legal/Compliance department\n"
        elif "budget" in po.blocked_reason.lower():
            analysis += "  • **Action Required:** Verify budget availability\n"
            analysis += "  • **Contact:** Finance department for budget clearance\n"
        else:
            analysis += "  • **Action Required:** Review and resolve blocking issue\n"
            analysis += "  • **Contact:** Department manager or procurement team\n"
        
        return analysis
    
    def _analyze_gr_block(self, gr) -> str:
        """Analyze root cause of GR block"""
        analysis = "  📊 **Analysis:**\n"
        
        # Check common GR block reasons
        if "quantity" in gr.blocked_reason.lower() or "discrepancy" in gr.blocked_reason.lower():
            analysis += "  • **Root Cause:** Quantity mismatch between PO and received goods\n"
            analysis += "  • **Action Required:** Verify actual quantities received\n"
            analysis += "  • **Resolution:** Contact vendor or update GR with correct quantities\n"
            analysis += "  • **Contact:** Warehouse manager and vendor\n"
        elif "quality" in gr.blocked_reason.lower():
            analysis += "  • **Root Cause:** Quality check failed\n"
            analysis += "  • **Action Required:** Inspect goods and document defects\n"
            analysis += "  • **Resolution:** Return to vendor or accept with adjustment\n"
            analysis += "  • **Contact:** Quality assurance team and vendor\n"
        elif "damage" in gr.blocked_reason.lower():
            analysis += "  • **Root Cause:** Damaged goods received\n"
            analysis += "  • **Action Required:** Document damage and assess\n"
            analysis += "  • **Resolution:** File claim or request replacement\n"
            analysis += "  • **Contact:** Shipping carrier and vendor\n"
        else:
            analysis += "  • **Action Required:** Investigate and resolve blocking issue\n"
            analysis += "  • **Contact:** Warehouse manager or receiving team\n"
        
        return analysis
    
    def _analyze_invoice_block(self, inv) -> str:
        """Analyze root cause of invoice block"""
        analysis = "  📊 **Analysis:**\n"
        
        # Get related PO and GR for three-way matching
        po = self.workflow.purchase_orders.get(inv.po_id)
        gr = self.workflow.goods_receipts.get(inv.gr_id)
        
        # Check common invoice block reasons
        if "pricing" in inv.blocked_reason.lower() or "price" in inv.blocked_reason.lower():
            analysis += "  • **Root Cause:** Price discrepancy detected\n"
            if po:
                po_total = po.total_amount
                inv_total = inv.total_amount
                diff = abs(po_total - inv_total)
                variance = (diff / po_total * 100) if po_total > 0 else 0
                
                analysis += f"  • **PO Amount:** ${po_total:,.2f}\n"
                analysis += f"  • **Invoice Amount:** ${inv_total:,.2f}\n"
                analysis += f"  • **Variance:** ${diff:,.2f} ({variance:.1f}%)\n"
                
                if variance > 10:
                    analysis += "  • **Severity:** HIGH - Variance exceeds 10% tolerance\n"
                elif variance > 5:
                    analysis += "  • **Severity:** MEDIUM - Variance exceeds 5% tolerance\n"
                else:
                    analysis += "  • **Severity:** LOW - Minor variance detected\n"
            
            analysis += "  • **Action Required:** Validate invoice line items against PO\n"
            analysis += "  • **Resolution:** Contact vendor for corrected invoice or approve variance\n"
            analysis += "  • **Contact:** Accounts Payable and vendor\n"
            
        elif "three-way" in inv.blocked_reason.lower() or "matching" in inv.blocked_reason.lower():
            analysis += "  • **Root Cause:** Three-way matching failure\n"
            analysis += "  • **Three-Way Match Components:**\n"
            analysis += f"    - Purchase Order: {inv.po_number}\n"
            analysis += f"    - Goods Receipt: {inv.gr_number}\n"
            analysis += f"    - Invoice: {inv.invoice_number}\n"
            analysis += "  • **Action Required:** Verify all documents match\n"
            analysis += "  • **Resolution:** Reconcile discrepancies between PO, GR, and Invoice\n"
            analysis += "  • **Contact:** Procurement, Warehouse, and AP teams\n"
            
        elif "authorization" in inv.blocked_reason.lower() or "approval" in inv.blocked_reason.lower():
            analysis += "  • **Root Cause:** Missing authorization or approval\n"
            
            # Check approval policy
            policy = self.workflow.get_applicable_policy(inv.total_amount)
            if policy:
                analysis += f"  • **Required Approvers:** {', '.join(policy.required_approvers)}\n"
                
                if inv.approvals:
                    approved = [a.approver for a in inv.approvals if a.status == "Approved"]
                    pending = [a.approver for a in inv.approvals if a.status == "Pending"]
                    
                    if approved:
                        analysis += f"  • **Approved By:** {', '.join(approved)}\n"
                    if pending:
                        analysis += f"  • **Awaiting:** {', '.join(pending)}\n"
            
            analysis += "  • **Action Required:** Obtain missing approvals\n"
            analysis += "  • **Resolution:** Route for approval or escalate\n"
            analysis += "  • **Contact:** Required approvers listed above\n"
            
        elif "tax" in inv.blocked_reason.lower():
            analysis += "  • **Root Cause:** Tax calculation issue\n"
            analysis += "  • **Action Required:** Verify tax rates and amounts\n"
            analysis += "  • **Resolution:** Correct tax calculation or obtain tax exemption\n"
            analysis += "  • **Contact:** Tax department and vendor\n"
            
        else:
            analysis += "  • **Action Required:** Investigate and resolve blocking issue\n"
            analysis += "  • **Resolution:** Review invoice details and unblock\n"
            analysis += "  • **Contact:** Accounts Payable manager\n"
        
        # Add due date warning if applicable
        if inv.due_date:
            now = datetime.now()
            days_until_due = (inv.due_date - now).days
            
            if days_until_due < 0:
                analysis += f"  ⚠️ **URGENT:** Invoice is {abs(days_until_due)} days overdue!\n"
            elif days_until_due < 7:
                analysis += f"  ⚡ **Priority:** Invoice due in {days_until_due} days\n"
        
        return analysis
    
    def _explain_p2p_process(self) -> dict:
        """Explain P2P process"""
        response = "📖 **Purchase-to-Pay (P2P) Process**\n\n"
        response += "The P2P workflow follows these steps:\n\n"
        response += "1️⃣ **Purchase Order (PO)** - Created by requester\n"
        response += "2️⃣ **Approval** - Routed based on amount thresholds\n"
        response += "3️⃣ **Goods Receipt (GR)** - Record delivery of goods/services\n"
        response += "4️⃣ **Quality Check** - Validate received items\n"
        response += "5️⃣ **Invoice** - Vendor submits invoice\n"
        response += "6️⃣ **Invoice Approval** - Finance validates invoice\n"
        response += "7️⃣ **Payment** - Process payment to vendor\n\n"
        response += "This ensures proper authorization and validation at each step!"
        
        return {'message': response}
    
    def _explain_approval_process(self) -> dict:
        """Explain approval process"""
        response = "✅ **Approval Process**\n\n"
        response += "Approvals are required based on purchase amount:\n\n"
        response += "💚 **Low Value** ($0 - $1,000)\n"
        response += "  • Department Manager approval\n\n"
        response += "💙 **Medium Value** ($1,000 - $10,000)\n"
        response += "  • Department Manager\n"
        response += "  • Finance Manager\n\n"
        response += "❤️ **High Value** (Over $10,000)\n"
        response += "  • Department Manager\n"
        response += "  • Finance Manager\n"
        response += "  • CFO/Executive\n\n"
        response += "Each approval level must be completed before proceeding!"
        
        return {'message': response}
    
    def _explain_three_way_matching(self) -> dict:
        """Explain three-way matching"""
        response = "🔗 **Three-Way Matching**\n\n"
        response += "Ensures payment accuracy by matching:\n\n"
        response += "1️⃣ **Purchase Order** - What was ordered\n"
        response += "2️⃣ **Goods Receipt** - What was received\n"
        response += "3️⃣ **Invoice** - What the vendor is charging\n\n"
        response += "✅ All three must match before payment is authorized.\n"
        response += "This prevents overpayment and ensures goods were received!"
        
        return {'message': response}
    
    def _handle_why_question(self, message: str) -> dict:
        """Handle 'why' questions about specific documents"""
        # Extract document number
        words = message.split()
        doc_num = None
        
        for word in words:
            if 'PO-' in word.upper() or 'GR-' in word.upper() or 'INV-' in word.upper():
                doc_num = word.upper()
                break
        
        if not doc_num:
            return {'message': "Please specify a document number (e.g., 'why is invoice INV-12345 blocked?')"}
        
        # Check if asking about blocked status
        if 'blocked' in message:
            # Search for the document
            # Check invoices first
            for inv in self.workflow.invoices.values():
                if doc_num in inv.invoice_number:
                    if inv.status.value == "Blocked":
                        response = f"🚫 **Why is {inv.invoice_number} Blocked?**\n\n"
                        response += f"**Invoice:** {inv.invoice_number}\n"
                        response += f"**Vendor:** {inv.vendor_name}\n"
                        response += f"**Amount:** ${inv.total_amount:,.2f}\n"
                        response += f"**Status:** {inv.status.value}\n"
                        response += f"**Blocked Reason:** {inv.blocked_reason}\n\n"
                        response += self._analyze_invoice_block(inv)
                        return {'message': response}
                    else:
                        return {'message': f"Invoice {inv.invoice_number} is not blocked. Current status: {inv.status.value}"}
            
            # Check POs
            for po in self.workflow.purchase_orders.values():
                if doc_num in po.po_number:
                    if po.status.value == "Blocked":
                        response = f"🚫 **Why is {po.po_number} Blocked?**\n\n"
                        response += f"**PO:** {po.po_number}\n"
                        response += f"**Vendor:** {po.vendor_name}\n"
                        response += f"**Amount:** ${po.total_amount:,.2f}\n"
                        response += f"**Status:** {po.status.value}\n"
                        response += f"**Blocked Reason:** {po.blocked_reason}\n\n"
                        response += self._analyze_po_block(po)
                        return {'message': response}
                    else:
                        return {'message': f"Purchase Order {po.po_number} is not blocked. Current status: {po.status.value}"}
            
            # Check GRs
            for gr in self.workflow.goods_receipts.values():
                if doc_num in gr.gr_number:
                    if gr.status.value == "Blocked":
                        response = f"🚫 **Why is {gr.gr_number} Blocked?**\n\n"
                        response += f"**GR:** {gr.gr_number}\n"
                        response += f"**PO:** {gr.po_number}\n"
                        response += f"**Amount:** ${gr.total_amount:,.2f}\n"
                        response += f"**Status:** {gr.status.value}\n"
                        response += f"**Blocked Reason:** {gr.blocked_reason}\n\n"
                        response += self._analyze_gr_block(gr)
                        return {'message': response}
                    else:
                        return {'message': f"Goods Receipt {gr.gr_number} is not blocked. Current status: {gr.status.value}"}
            
            return {'message': f"❌ Document **{doc_num}** not found. Please check the number and try again."}
        
        # If not asking about blocked, fall back to search
        return self._search_documents(message)
    
    def _search_documents(self, message: str) -> dict:
        """Search for documents"""
        # Extract potential document number
        words = message.split()
        doc_num = None
        
        for word in words:
            if 'PO-' in word.upper() or 'GR-' in word.upper() or 'INV-' in word.upper():
                doc_num = word.upper()
                break
        
        if not doc_num:
            return {'message': "Please specify a document number (e.g., 'find PO-12345')"}
        
        # Search in POs
        for po in self.workflow.purchase_orders.values():
            if doc_num in po.po_number:
                response = f"📋 **Purchase Order: {po.po_number}**\n\n"
                response += f"**Vendor:** {po.vendor_name}\n"
                response += f"**Requester:** {po.requester} ({po.department})\n"
                response += f"**Amount:** ${po.total_amount:,.2f}\n"
                response += f"**Status:** {po.status.value}\n"
                response += f"**Created:** {po.creation_date.strftime('%Y-%m-%d')}\n"
                return {'message': response, 'po_id': po.id}
        
        # Search in GRs
        for gr in self.workflow.goods_receipts.values():
            if doc_num in gr.gr_number:
                response = f"📦 **Goods Receipt: {gr.gr_number}**\n\n"
                response += f"**Related PO:** {gr.po_number}\n"
                response += f"**Received By:** {gr.received_by}\n"
                response += f"**Amount:** ${gr.total_amount:,.2f}\n"
                response += f"**Status:** {gr.status.value}\n"
                return {'message': response, 'gr_id': gr.id}
        
        # Search in Invoices
        for inv in self.workflow.invoices.values():
            if doc_num in inv.invoice_number:
                response = f"🧾 **Invoice: {inv.invoice_number}**\n\n"
                response += f"**Vendor:** {inv.vendor_name}\n"
                response += f"**Amount:** ${inv.total_amount:,.2f}\n"
                response += f"**Status:** {inv.status.value}\n"
                response += f"**Due Date:** {inv.due_date.strftime('%Y-%m-%d')}\n"
                return {'message': response, 'invoice_id': inv.id}
        
        return {'message': f"❌ Document **{doc_num}** not found. Please check the number and try again."}
    
    def _get_payment_info(self) -> dict:
        """Get payment information"""
        paid_count = sum(1 for inv in self.workflow.invoices.values() 
                        if inv.status.value == 'Paid')
        total_paid = sum(inv.total_amount for inv in self.workflow.invoices.values() 
                        if inv.status.value == 'Paid')
        
        response = f"💳 **Payment Information**\n\n"
        response += f"**Paid Invoices:** {paid_count}\n"
        response += f"**Total Paid:** ${total_paid:,.2f}\n"
        
        return {'message': response}
    
    def _get_overdue_info(self) -> dict:
        """Get overdue invoice information"""
        now = datetime.now()
        overdue = [inv for inv in self.workflow.invoices.values() 
                  if inv.status.value == 'Approved' and inv.due_date < now]
        
        response = f"⚠️ **Overdue Invoices**\n\n"
        if len(overdue) == 0:
            response += "✅ No overdue invoices. All payments are on track!"
        else:
            response += f"**Count:** {len(overdue)} invoices overdue\n\n"
            for inv in overdue[:5]:
                days_overdue = (now - inv.due_date).days
                response += f"• {inv.invoice_number} - ${inv.total_amount:,.2f} ({days_overdue} days overdue)\n"
        
        return {'message': response}
    
    def _list_vendors(self) -> dict:
        """List vendors"""
        vendors = set()
        for po in self.workflow.purchase_orders.values():
            vendors.add((po.vendor_id, po.vendor_name))
        
        response = f"🏢 **Vendors ({len(vendors)} total)**\n\n"
        for vid, vname in sorted(vendors):
            response += f"• {vid}: {vname}\n"
        
        return {'message': response}
    
    def _get_blocked_invoices_only(self) -> dict:
        """Get only blocked invoices with detailed analysis"""
        blocked = self.workflow.get_blocked_documents()
        blocked_invs = blocked['invoices']
        
        if len(blocked_invs) == 0:
            return {'message': "✅ **No blocked invoices!** All invoices are processing normally."}
        
        response = f"🚫 **Blocked Invoices** ({len(blocked_invs)} found)\n\n"
        
        for inv in blocked_invs:
            response += f"**{inv.invoice_number}** - {inv.vendor_name}\n"
            response += f"💰 Amount: ${inv.total_amount:,.2f}\n"
            response += f"🚫 Blocked Reason: {inv.blocked_reason}\n"
            response += self._analyze_invoice_block(inv)
            response += "\n" + "-"*50 + "\n\n"
        
        return {'message': response}
    
    def _get_blocked_pos_only(self) -> dict:
        """Get only blocked purchase orders"""
        blocked = self.workflow.get_blocked_documents()
        blocked_pos = blocked['purchase_orders']
        
        if len(blocked_pos) == 0:
            return {'message': "✅ **No blocked purchase orders!** All POs are processing normally."}
        
        response = f"🚫 **Blocked Purchase Orders** ({len(blocked_pos)} found)\n\n"
        
        for po in blocked_pos:
            response += f"**{po.po_number}** - {po.vendor_name}\n"
            response += f"💰 Amount: ${po.total_amount:,.2f}\n"
            response += f"🚫 Blocked Reason: {po.blocked_reason}\n"
            response += self._analyze_po_block(po)
            response += "\n" + "-"*50 + "\n\n"
        
        return {'message': response}
    
    def _get_blocked_grs_only(self) -> dict:
        """Get only blocked goods receipts"""
        blocked = self.workflow.get_blocked_documents()
        blocked_grs = blocked['goods_receipts']
        
        if len(blocked_grs) == 0:
            return {'message': "✅ **No blocked goods receipts!** All GRs are processing normally."}
        
        response = f"🚫 **Blocked Goods Receipts** ({len(blocked_grs)} found)\n\n"
        
        for gr in blocked_grs:
            response += f"**{gr.gr_number}** (PO: {gr.po_number})\n"
            response += f"💰 Amount: ${gr.total_amount:,.2f}\n"
            response += f"🚫 Blocked Reason: {gr.blocked_reason}\n"
            response += self._analyze_gr_block(gr)
            response += "\n" + "-"*50 + "\n\n"
        
        return {'message': response}
    
    def _get_pending_invoices_only(self) -> dict:
        """Get only pending invoices"""
        pending = self.workflow.get_all_pending_approvals()
        pending_invs = pending['invoices']
        
        if len(pending_invs) == 0:
            return {'message': "✅ **No pending invoices!** All invoices are either approved or in other statuses."}
        
        response = f"⏳ **Pending Invoices** ({len(pending_invs)} awaiting approval)\n\n"
        
        for inv in pending_invs:
            response += f"**{inv.invoice_number}** - {inv.vendor_name}\n"
            response += f"💰 Amount: ${inv.total_amount:,.2f}\n"
            response += f"📅 Due: {inv.due_date.strftime('%Y-%m-%d')}\n"
            
            # Show approval status
            if inv.approvals:
                response += "👥 Approval Status:\n"
                for approval in inv.approvals:
                    status_icon = "✅" if approval.status == "Approved" else "⏳" if approval.status == "Pending" else "❌"
                    response += f"  {status_icon} {approval.approver}: {approval.status}\n"
            
            response += "\n"
        
        return {'message': response}
    
    def _get_pending_pos_only(self) -> dict:
        """Get only pending purchase orders"""
        pending = self.workflow.get_all_pending_approvals()
        pending_pos = pending['purchase_orders']
        
        if len(pending_pos) == 0:
            return {'message': "✅ **No pending purchase orders!** All POs are either approved or in other statuses."}
        
        response = f"⏳ **Pending Purchase Orders** ({len(pending_pos)} awaiting approval)\n\n"
        
        for po in pending_pos:
            response += f"**{po.po_number}** - {po.vendor_name}\n"
            response += f"👤 Requester: {po.requester} ({po.department})\n"
            response += f"💰 Amount: ${po.total_amount:,.2f}\n"
            
            # Show approval status
            if po.approvals:
                response += "👥 Approval Status:\n"
                for approval in po.approvals:
                    status_icon = "✅" if approval.status == "Approved" else "⏳" if approval.status == "Pending" else "❌"
                    response += f"  {status_icon} {approval.approver}: {approval.status}\n"
            
            response += "\n"
        
        return {'message': response}
