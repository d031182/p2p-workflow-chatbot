"""
Business logic and workflow for Purchase-to-Pay process
"""
from typing import List, Optional, Dict
from models import (
    PurchaseOrder, GoodsReceipt, Invoice, LineItem,
    ApprovalPolicy, POStatus, GRStatus, InvoiceStatus, PaymentTerms
)
import copy


class P2PWorkflow:
    """Purchase-to-Pay workflow manager"""
    
    def __init__(self):
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.goods_receipts: Dict[str, GoodsReceipt] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.approval_policies: List[ApprovalPolicy] = []
    
    def add_approval_policy(self, policy: ApprovalPolicy):
        """Add an approval policy"""
        self.approval_policies.append(policy)
        # Sort policies by min_amount to ensure correct matching
        self.approval_policies.sort(key=lambda p: p.min_amount)
    
    def get_applicable_policy(self, amount: float) -> Optional[ApprovalPolicy]:
        """Get the applicable approval policy for a given amount"""
        for policy in reversed(self.approval_policies):
            if policy.is_applicable(amount):
                return policy
        return None
    
    def create_purchase_order(
        self,
        vendor_id: str,
        vendor_name: str,
        requester: str,
        department: str,
        line_items: List[LineItem],
        payment_terms: PaymentTerms = PaymentTerms.NET_30,
        delivery_address: str = "",
        notes: str = ""
    ) -> PurchaseOrder:
        """Create a new purchase order"""
        po = PurchaseOrder(
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            requester=requester,
            department=department,
            payment_terms=payment_terms,
            delivery_address=delivery_address,
            notes=notes
        )
        
        for item in line_items:
            po.add_line_item(item)
        
        self.purchase_orders[po.id] = po
        return po
    
    def submit_po_for_approval(self, po_id: str) -> bool:
        """Submit PO for approval based on approval policies"""
        po = self.purchase_orders.get(po_id)
        if not po:
            return False
        
        if po.status != POStatus.DRAFT:
            return False
        
        policy = self.get_applicable_policy(po.total_amount)
        if not policy:
            # No policy applicable, auto-approve
            po.status = POStatus.APPROVED
            return True
        
        po.submit_for_approval(policy)
        return True
    
    def approve_po(self, po_id: str, approver: str, comments: str = "") -> bool:
        """Approve a purchase order"""
        po = self.purchase_orders.get(po_id)
        if not po or po.status != POStatus.PENDING_APPROVAL:
            return False
        
        po.approve(approver, comments)
        
        # If fully approved, mark as approved
        if po.status == POStatus.APPROVED:
            po.status = POStatus.APPROVED
        
        return True
    
    def reject_po(self, po_id: str, approver: str, comments: str = "") -> bool:
        """Reject a purchase order"""
        po = self.purchase_orders.get(po_id)
        if not po or po.status != POStatus.PENDING_APPROVAL:
            return False
        
        po.reject(approver, comments)
        return True
    
    def create_goods_receipt(
        self,
        po_id: str,
        received_by: str,
        line_items: List[LineItem],
        notes: str = ""
    ) -> Optional[GoodsReceipt]:
        """Create a goods receipt for an approved PO"""
        po = self.purchase_orders.get(po_id)
        if not po or po.status != POStatus.APPROVED:
            return None
        
        gr = GoodsReceipt(
            po_id=po.id,
            po_number=po.po_number,
            received_by=received_by,
            notes=notes
        )
        
        for item in line_items:
            gr.line_items.append(item)
        
        gr.receive_goods()
        self.goods_receipts[gr.id] = gr
        
        # Update PO status
        po.status = POStatus.IN_PROGRESS
        
        return gr
    
    def perform_quality_check(
        self,
        gr_id: str,
        checker: str,
        passed: bool
    ) -> bool:
        """Perform quality check on goods receipt"""
        gr = self.goods_receipts.get(gr_id)
        if not gr or gr.status != GRStatus.RECEIVED:
            return False
        
        gr.perform_quality_check(checker, passed)
        
        # Update PO status if goods accepted
        if passed:
            po = self.purchase_orders.get(gr.po_id)
            if po:
                # Check if all GRs for this PO are accepted
                po_grs = [g for g in self.goods_receipts.values() if g.po_id == po.id]
                if all(g.status == GRStatus.ACCEPTED for g in po_grs):
                    po.status = POStatus.COMPLETED
        
        return True
    
    def create_invoice(
        self,
        po_id: str,
        gr_id: str,
        vendor_id: str,
        vendor_name: str,
        line_items: List[LineItem],
        payment_terms: Optional[PaymentTerms] = None,
        notes: str = ""
    ) -> Optional[Invoice]:
        """Create an invoice based on GR and PO"""
        po = self.purchase_orders.get(po_id)
        gr = self.goods_receipts.get(gr_id)
        
        if not po or not gr:
            return None
        
        if gr.status != GRStatus.ACCEPTED:
            return None
        
        # Use PO payment terms if not specified
        if payment_terms is None:
            payment_terms = po.payment_terms
        
        invoice = Invoice(
            po_id=po.id,
            po_number=po.po_number,
            gr_id=gr.id,
            gr_number=gr.gr_number,
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            payment_terms=payment_terms,
            notes=notes
        )
        
        for item in line_items:
            invoice.line_items.append(item)
        
        self.invoices[invoice.id] = invoice
        return invoice
    
    def submit_invoice_for_approval(self, invoice_id: str) -> bool:
        """Submit invoice for approval"""
        invoice = self.invoices.get(invoice_id)
        if not invoice or invoice.status != InvoiceStatus.DRAFT:
            return False
        
        policy = self.get_applicable_policy(invoice.total_amount)
        if not policy:
            # No policy applicable, auto-approve
            invoice.status = InvoiceStatus.APPROVED
            return True
        
        invoice.submit_for_approval(policy)
        return True
    
    def approve_invoice(self, invoice_id: str, approver: str, comments: str = "") -> bool:
        """Approve an invoice"""
        invoice = self.invoices.get(invoice_id)
        if not invoice or invoice.status != InvoiceStatus.PENDING_APPROVAL:
            return False
        
        invoice.approve(approver, comments)
        return True
    
    def pay_invoice(self, invoice_id: str) -> bool:
        """Mark invoice as paid"""
        invoice = self.invoices.get(invoice_id)
        if not invoice or invoice.status != InvoiceStatus.APPROVED:
            return False
        
        invoice.mark_as_paid()
        return True
    
    def check_overdue_invoices(self):
        """Check and update status of overdue invoices"""
        for invoice in self.invoices.values():
            invoice.check_overdue()
    
    def get_po_summary(self, po_id: str) -> Optional[Dict]:
        """Get summary of a purchase order and its related documents"""
        po = self.purchase_orders.get(po_id)
        if not po:
            return None
        
        related_grs = [gr for gr in self.goods_receipts.values() if gr.po_id == po_id]
        related_invoices = [inv for inv in self.invoices.values() if inv.po_id == po_id]
        
        return {
            'purchase_order': po,
            'goods_receipts': related_grs,
            'invoices': related_invoices,
            'total_received': sum(gr.total_amount for gr in related_grs if gr.status == GRStatus.ACCEPTED),
            'total_invoiced': sum(inv.total_amount for inv in related_invoices),
            'total_paid': sum(inv.total_amount for inv in related_invoices if inv.status == InvoiceStatus.PAID)
        }
    
    def get_all_pending_approvals(self) -> Dict:
        """Get all documents pending approval"""
        pending_pos = [po for po in self.purchase_orders.values() 
                      if po.status == POStatus.PENDING_APPROVAL]
        pending_invoices = [inv for inv in self.invoices.values() 
                           if inv.status == InvoiceStatus.PENDING_APPROVAL]
        
        return {
            'purchase_orders': pending_pos,
            'invoices': pending_invoices
        }
    
    def block_po(self, po_id: str, reason: str) -> bool:
        """Block a purchase order with a reason"""
        po = self.purchase_orders.get(po_id)
        if not po:
            return False
        po.status = POStatus.BLOCKED
        po.blocked_reason = reason
        return True
    
    def block_gr(self, gr_id: str, reason: str) -> bool:
        """Block a goods receipt with a reason"""
        gr = self.goods_receipts.get(gr_id)
        if not gr:
            return False
        gr.status = GRStatus.BLOCKED
        gr.blocked_reason = reason
        return True
    
    def block_invoice(self, invoice_id: str, reason: str) -> bool:
        """Block an invoice with a reason"""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return False
        invoice.block(reason)
        return True
    
    def unblock_invoice(self, invoice_id: str) -> bool:
        """Unblock an invoice"""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return False
        invoice.unblock()
        return True
    
    def get_blocked_documents(self) -> Dict:
        """Get all blocked documents"""
        blocked_pos = [po for po in self.purchase_orders.values() 
                      if po.status == POStatus.BLOCKED]
        blocked_grs = [gr for gr in self.goods_receipts.values() 
                      if gr.status == GRStatus.BLOCKED]
        blocked_invoices = [inv for inv in self.invoices.values() 
                           if inv.status == InvoiceStatus.BLOCKED]
        
        return {
            'purchase_orders': blocked_pos,
            'goods_receipts': blocked_grs,
            'invoices': blocked_invoices
        }
    
    def get_statistics(self) -> Dict:
        """Get overall workflow statistics"""
        return {
            'total_pos': len(self.purchase_orders),
            'approved_pos': len([po for po in self.purchase_orders.values() 
                                if po.status == POStatus.APPROVED]),
            'pending_pos': len([po for po in self.purchase_orders.values() 
                               if po.status == POStatus.PENDING_APPROVAL]),
            'blocked_pos': len([po for po in self.purchase_orders.values() 
                               if po.status == POStatus.BLOCKED]),
            'total_grs': len(self.goods_receipts),
            'accepted_grs': len([gr for gr in self.goods_receipts.values() 
                                if gr.status == GRStatus.ACCEPTED]),
            'blocked_grs': len([gr for gr in self.goods_receipts.values() 
                               if gr.status == GRStatus.BLOCKED]),
            'total_invoices': len(self.invoices),
            'paid_invoices': len([inv for inv in self.invoices.values() 
                                 if inv.status == InvoiceStatus.PAID]),
            'overdue_invoices': len([inv for inv in self.invoices.values() 
                                    if inv.status == InvoiceStatus.OVERDUE]),
            'blocked_invoices': len([inv for inv in self.invoices.values() 
                                    if inv.status == InvoiceStatus.BLOCKED]),
            'total_spend': sum(inv.total_amount for inv in self.invoices.values() 
                              if inv.status == InvoiceStatus.PAID)
        }
