"""
Data models for Purchase-to-Pay business process
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
import uuid


class POStatus(Enum):
    """Purchase Order status"""
    DRAFT = "Draft"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    BLOCKED = "Blocked"


class GRStatus(Enum):
    """Goods Receipt status"""
    DRAFT = "Draft"
    RECEIVED = "Received"
    QUALITY_CHECK = "Quality Check"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    BLOCKED = "Blocked"


class InvoiceStatus(Enum):
    """Invoice status"""
    DRAFT = "Draft"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"
    OVERDUE = "Overdue"
    BLOCKED = "Blocked"


class PaymentTerms(Enum):
    """Payment terms"""
    NET_30 = "Net 30 Days"
    NET_60 = "Net 60 Days"
    NET_90 = "Net 90 Days"
    IMMEDIATE = "Immediate"
    DUE_ON_RECEIPT = "Due on Receipt"


@dataclass
class ApprovalPolicy:
    """Approval policy configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    min_amount: float = 0.0
    max_amount: float = float('inf')
    required_approvers: List[str] = field(default_factory=list)
    approval_levels: int = 1
    
    def is_applicable(self, amount: float) -> bool:
        """Check if policy applies to given amount"""
        return self.min_amount <= amount <= self.max_amount


@dataclass
class ApprovalRecord:
    """Individual approval record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    approver: str = ""
    status: str = "Pending"  # Pending, Approved, Rejected
    comments: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LineItem:
    """Line item for PO/Invoice"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    item_code: str = ""
    description: str = ""
    quantity: float = 0.0
    unit_price: float = 0.0
    tax_rate: float = 0.0
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price
    
    @property
    def tax_amount(self) -> float:
        return self.subtotal * self.tax_rate
    
    @property
    def total(self) -> float:
        return self.subtotal + self.tax_amount


@dataclass
class PurchaseOrder:
    """Purchase Order"""
    id: str = field(default_factory=lambda: f"PO-{uuid.uuid4().hex[:8].upper()}")
    po_number: str = ""
    vendor_id: str = ""
    vendor_name: str = ""
    requester: str = ""
    department: str = ""
    status: POStatus = POStatus.DRAFT
    creation_date: datetime = field(default_factory=datetime.now)
    approval_date: Optional[datetime] = None
    line_items: List[LineItem] = field(default_factory=list)
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    delivery_address: str = ""
    notes: str = ""
    approvals: List[ApprovalRecord] = field(default_factory=list)
    applicable_policy: Optional[ApprovalPolicy] = None
    blocked_reason: str = ""
    
    def __post_init__(self):
        if not self.po_number:
            self.po_number = self.id
    
    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.line_items)
    
    @property
    def tax_total(self) -> float:
        return sum(item.tax_amount for item in self.line_items)
    
    @property
    def total_amount(self) -> float:
        return sum(item.total for item in self.line_items)
    
    def add_line_item(self, item: LineItem):
        """Add a line item to the PO"""
        self.line_items.append(item)
    
    def submit_for_approval(self, policy: ApprovalPolicy):
        """Submit PO for approval"""
        self.status = POStatus.PENDING_APPROVAL
        self.applicable_policy = policy
        for approver in policy.required_approvers:
            self.approvals.append(ApprovalRecord(approver=approver))
    
    def approve(self, approver: str, comments: str = ""):
        """Approve the PO"""
        for approval in self.approvals:
            if approval.approver == approver and approval.status == "Pending":
                approval.status = "Approved"
                approval.comments = comments
                approval.timestamp = datetime.now()
                break
        
        # Check if all approvals are completed
        if all(a.status == "Approved" for a in self.approvals):
            self.status = POStatus.APPROVED
            self.approval_date = datetime.now()
    
    def reject(self, approver: str, comments: str = ""):
        """Reject the PO"""
        for approval in self.approvals:
            if approval.approver == approver and approval.status == "Pending":
                approval.status = "Rejected"
                approval.comments = comments
                approval.timestamp = datetime.now()
                break
        self.status = POStatus.REJECTED


@dataclass
class GoodsReceipt:
    """Goods Receipt"""
    id: str = field(default_factory=lambda: f"GR-{uuid.uuid4().hex[:8].upper()}")
    gr_number: str = ""
    po_id: str = ""
    po_number: str = ""
    status: GRStatus = GRStatus.DRAFT
    receipt_date: datetime = field(default_factory=datetime.now)
    received_by: str = ""
    line_items: List[LineItem] = field(default_factory=list)
    notes: str = ""
    quality_checked: bool = False
    quality_checker: str = ""
    quality_check_date: Optional[datetime] = None
    blocked_reason: str = ""
    
    def __post_init__(self):
        if not self.gr_number:
            self.gr_number = self.id
    
    @property
    def total_amount(self) -> float:
        return sum(item.total for item in self.line_items)
    
    def receive_goods(self):
        """Mark goods as received"""
        self.status = GRStatus.RECEIVED
        self.receipt_date = datetime.now()
    
    def perform_quality_check(self, checker: str, passed: bool):
        """Perform quality check"""
        self.quality_checked = True
        self.quality_checker = checker
        self.quality_check_date = datetime.now()
        
        if passed:
            self.status = GRStatus.ACCEPTED
        else:
            self.status = GRStatus.REJECTED


@dataclass
class Invoice:
    """Invoice"""
    id: str = field(default_factory=lambda: f"INV-{uuid.uuid4().hex[:8].upper()}")
    invoice_number: str = ""
    po_id: str = ""
    po_number: str = ""
    gr_id: str = ""
    gr_number: str = ""
    vendor_id: str = ""
    vendor_name: str = ""
    status: InvoiceStatus = InvoiceStatus.DRAFT
    invoice_date: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    line_items: List[LineItem] = field(default_factory=list)
    notes: str = ""
    approvals: List[ApprovalRecord] = field(default_factory=list)
    applicable_policy: Optional[ApprovalPolicy] = None
    blocked_reason: str = ""
    
    def __post_init__(self):
        if not self.invoice_number:
            self.invoice_number = self.id
        if not self.due_date:
            self.calculate_due_date()
    
    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.line_items)
    
    @property
    def tax_total(self) -> float:
        return sum(item.tax_amount for item in self.line_items)
    
    @property
    def total_amount(self) -> float:
        return sum(item.total for item in self.line_items)
    
    def calculate_due_date(self):
        """Calculate due date based on payment terms"""
        days_map = {
            PaymentTerms.IMMEDIATE: 0,
            PaymentTerms.DUE_ON_RECEIPT: 0,
            PaymentTerms.NET_30: 30,
            PaymentTerms.NET_60: 60,
            PaymentTerms.NET_90: 90
        }
        days = days_map.get(self.payment_terms, 30)
        self.due_date = self.invoice_date + timedelta(days=days)
    
    def submit_for_approval(self, policy: ApprovalPolicy):
        """Submit invoice for approval"""
        self.status = InvoiceStatus.PENDING_APPROVAL
        self.applicable_policy = policy
        for approver in policy.required_approvers:
            self.approvals.append(ApprovalRecord(approver=approver))
    
    def approve(self, approver: str, comments: str = ""):
        """Approve the invoice"""
        for approval in self.approvals:
            if approval.approver == approver and approval.status == "Pending":
                approval.status = "Approved"
                approval.comments = comments
                approval.timestamp = datetime.now()
                break
        
        # Check if all approvals are completed
        if all(a.status == "Approved" for a in self.approvals):
            self.status = InvoiceStatus.APPROVED
    
    def mark_as_paid(self):
        """Mark invoice as paid"""
        self.status = InvoiceStatus.PAID
        self.payment_date = datetime.now()
    
    def check_overdue(self):
        """Check if invoice is overdue"""
        if self.status == InvoiceStatus.APPROVED and self.due_date:
            if datetime.now() > self.due_date:
                self.status = InvoiceStatus.OVERDUE
    
    def block(self, reason: str):
        """Block the invoice with a reason"""
        self.status = InvoiceStatus.BLOCKED
        self.blocked_reason = reason
    
    def unblock(self):
        """Unblock the invoice"""
        if self.status == InvoiceStatus.BLOCKED:
            self.status = InvoiceStatus.DRAFT
            self.blocked_reason = ""
