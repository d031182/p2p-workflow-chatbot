"""
Sample data generator for P2P workflow demonstration
"""
from models import (
    LineItem, ApprovalPolicy, PaymentTerms
)
from workflow import P2PWorkflow
from datetime import datetime, timedelta
import random


def generate_sample_data() -> P2PWorkflow:
    """Generate comprehensive sample data for the P2P workflow"""
    
    workflow = P2PWorkflow()
    
    # Setup approval policies
    print("\n=== Setting up Approval Policies ===")
    
    # Policy 1: Low value purchases (0-1000)
    policy1 = ApprovalPolicy(
        name="Low Value Purchase Policy",
        description="For purchases up to $1,000 - requires department manager approval",
        min_amount=0.0,
        max_amount=1000.0,
        required_approvers=["John Smith (Dept Manager)"],
        approval_levels=1
    )
    workflow.add_approval_policy(policy1)
    print(f"✓ Added: {policy1.name} ($0 - $1,000)")
    
    # Policy 2: Medium value purchases (1000-10000)
    policy2 = ApprovalPolicy(
        name="Medium Value Purchase Policy",
        description="For purchases $1,000 - $10,000 - requires department and finance approval",
        min_amount=1000.01,
        max_amount=10000.0,
        required_approvers=["John Smith (Dept Manager)", "Sarah Johnson (Finance Manager)"],
        approval_levels=2
    )
    workflow.add_approval_policy(policy2)
    print(f"✓ Added: {policy2.name} ($1,000 - $10,000)")
    
    # Policy 3: High value purchases (10000+)
    policy3 = ApprovalPolicy(
        name="High Value Purchase Policy",
        description="For purchases over $10,000 - requires dept, finance, and executive approval",
        min_amount=10000.01,
        max_amount=float('inf'),
        required_approvers=[
            "John Smith (Dept Manager)",
            "Sarah Johnson (Finance Manager)",
            "Michael Brown (CFO)"
        ],
        approval_levels=3
    )
    workflow.add_approval_policy(policy3)
    print(f"✓ Added: {policy3.name} (Over $10,000)")
    
    print("\n=== Creating Purchase Orders ===")
    
    # PO 1: Low value - Office Supplies
    items1 = [
        LineItem(
            item_code="OFF-001",
            description="Premium Printer Paper (10 reams)",
            quantity=10,
            unit_price=25.99,
            tax_rate=0.10
        ),
        LineItem(
            item_code="OFF-002",
            description="Ballpoint Pens (Box of 50)",
            quantity=5,
            unit_price=12.50,
            tax_rate=0.10
        ),
        LineItem(
            item_code="OFF-003",
            description="Sticky Notes Assorted",
            quantity=20,
            unit_price=3.99,
            tax_rate=0.10
        )
    ]
    
    po1 = workflow.create_purchase_order(
        vendor_id="V001",
        vendor_name="Office Supplies Co.",
        requester="Alice Williams",
        department="Marketing",
        line_items=items1,
        payment_terms=PaymentTerms.NET_30,
        delivery_address="123 Business Plaza, Suite 400",
        notes="Urgent - needed for marketing campaign preparation"
    )
    print(f"✓ Created PO: {po1.po_number} - Office Supplies - ${po1.total_amount:.2f}")
    
    # PO 2: Medium value - Computer Equipment
    items2 = [
        LineItem(
            item_code="IT-101",
            description="Dell Latitude Laptop",
            quantity=3,
            unit_price=1299.99,
            tax_rate=0.10
        ),
        LineItem(
            item_code="IT-102",
            description="27-inch Monitor",
            quantity=3,
            unit_price=349.99,
            tax_rate=0.10
        ),
        LineItem(
            item_code="IT-103",
            description="Wireless Mouse & Keyboard Combo",
            quantity=3,
            unit_price=79.99,
            tax_rate=0.10
        )
    ]
    
    po2 = workflow.create_purchase_order(
        vendor_id="V002",
        vendor_name="Tech Solutions Inc.",
        requester="Bob Chen",
        department="IT",
        line_items=items2,
        payment_terms=PaymentTerms.NET_60,
        delivery_address="123 Business Plaza, IT Department",
        notes="New equipment for developers"
    )
    print(f"✓ Created PO: {po2.po_number} - Computer Equipment - ${po2.total_amount:.2f}")
    
    # PO 3: High value - Manufacturing Equipment
    items3 = [
        LineItem(
            item_code="MFG-501",
            description="Industrial 3D Printer",
            quantity=2,
            unit_price=8500.00,
            tax_rate=0.10
        ),
        LineItem(
            item_code="MFG-502",
            description="CNC Machine Maintenance Kit",
            quantity=1,
            unit_price=2500.00,
            tax_rate=0.10
        ),
        LineItem(
            item_code="MFG-503",
            description="Safety Equipment Bundle",
            quantity=10,
            unit_price=150.00,
            tax_rate=0.10
        )
    ]
    
    po3 = workflow.create_purchase_order(
        vendor_id="V003",
        vendor_name="Industrial Equipment Ltd.",
        requester="Carlos Rodriguez",
        department="Manufacturing",
        line_items=items3,
        payment_terms=PaymentTerms.NET_90,
        delivery_address="Manufacturing Plant - Building B",
        notes="Critical equipment for production line expansion"
    )
    print(f"✓ Created PO: {po3.po_number} - Manufacturing Equipment - ${po3.total_amount:.2f}")
    
    # PO 4: Consulting Services
    items4 = [
        LineItem(
            item_code="SVC-201",
            description="Business Process Consulting (40 hours)",
            quantity=40,
            unit_price=150.00,
            tax_rate=0.10
        ),
        LineItem(
            item_code="SVC-202",
            description="Training Materials",
            quantity=1,
            unit_price=500.00,
            tax_rate=0.10
        )
    ]
    
    po4 = workflow.create_purchase_order(
        vendor_id="V004",
        vendor_name="Business Consulting Group",
        requester="Diana Lee",
        department="Operations",
        line_items=items4,
        payment_terms=PaymentTerms.NET_30,
        delivery_address="123 Business Plaza, Conference Room A",
        notes="Q1 process improvement initiative"
    )
    print(f"✓ Created PO: {po4.po_number} - Consulting Services - ${po4.total_amount:.2f}")
    
    print("\n=== Processing Approvals ===")
    
    # Submit all POs for approval
    workflow.submit_po_for_approval(po1.id)
    print(f"✓ {po1.po_number} submitted for approval (Status: {po1.status.value})")
    
    workflow.submit_po_for_approval(po2.id)
    print(f"✓ {po2.po_number} submitted for approval (Status: {po2.status.value})")
    
    workflow.submit_po_for_approval(po3.id)
    print(f"✓ {po3.po_number} submitted for approval (Status: {po3.status.value})")
    
    workflow.submit_po_for_approval(po4.id)
    print(f"✓ {po4.po_number} submitted for approval (Status: {po4.status.value})")
    
    # Approve PO1 (single approver)
    workflow.approve_po(po1.id, "John Smith (Dept Manager)", "Approved - standard office supplies")
    print(f"✓ {po1.po_number} approved by John Smith (Status: {po1.status.value})")
    
    # Approve PO2 (two approvers)
    workflow.approve_po(po2.id, "John Smith (Dept Manager)", "Approved - needed for new team members")
    workflow.approve_po(po2.id, "Sarah Johnson (Finance Manager)", "Budget approved")
    print(f"✓ {po2.po_number} approved by all required approvers (Status: {po2.status.value})")
    
    # Approve PO3 (three approvers)
    workflow.approve_po(po3.id, "John Smith (Dept Manager)", "Critical for production")
    workflow.approve_po(po3.id, "Sarah Johnson (Finance Manager)", "Capital expenditure approved")
    workflow.approve_po(po3.id, "Michael Brown (CFO)", "Approved for strategic initiative")
    print(f"✓ {po3.po_number} approved by all required approvers (Status: {po3.status.value})")
    
    # Approve PO4 - but leave one approval pending
    workflow.approve_po(po4.id, "John Smith (Dept Manager)", "Approved for Q1 initiative")
    # Don't approve by Sarah yet - leave it pending
    print(f"✓ {po4.po_number} partially approved (Status: {po4.status.value})")
    
    print("\n=== Creating Goods Receipts ===")
    
    # Create GR for PO1
    gr1 = workflow.create_goods_receipt(
        po_id=po1.id,
        received_by="Warehouse Staff - Tom Anderson",
        line_items=items1,
        notes="All items received in good condition"
    )
    print(f"✓ Created GR: {gr1.gr_number} for {po1.po_number}")
    
    # Create GR for PO2
    gr2 = workflow.create_goods_receipt(
        po_id=po2.id,
        received_by="IT Department - Bob Chen",
        line_items=items2,
        notes="Equipment inspected upon arrival"
    )
    print(f"✓ Created GR: {gr2.gr_number} for {po2.po_number}")
    
    # Create GR for PO3
    gr3 = workflow.create_goods_receipt(
        po_id=po3.id,
        received_by="Manufacturing - Carlos Rodriguez",
        line_items=items3,
        notes="Equipment delivered and staged for installation"
    )
    print(f"✓ Created GR: {gr3.gr_number} for {po3.po_number}")
    
    # Note: Cannot create GR for PO4 yet - still pending approval
    print(f"✓ Skipping GR for {po4.po_number} - awaiting full approval")
    
    print("\n=== Performing Quality Checks ===")
    
    # Perform quality checks
    workflow.perform_quality_check(gr1.id, "Quality Team - Emma Davis", True)
    print(f"✓ Quality check passed for {gr1.gr_number}")
    
    workflow.perform_quality_check(gr2.id, "IT Quality - Bob Chen", True)
    print(f"✓ Quality check passed for {gr2.gr_number}")
    
    workflow.perform_quality_check(gr3.id, "Manufacturing QA - Carlos Rodriguez", True)
    print(f"✓ Quality check passed for {gr3.gr_number}")
    
    # No quality check for gr4 since it wasn't created
    
    print("\n=== Creating Invoices ===")
    
    # Create invoices
    inv1 = workflow.create_invoice(
        po_id=po1.id,
        gr_id=gr1.id,
        vendor_id="V001",
        vendor_name="Office Supplies Co.",
        line_items=items1,
        notes="Invoice for office supplies delivery"
    )
    print(f"✓ Created Invoice: {inv1.invoice_number} for {po1.po_number} - ${inv1.total_amount:.2f}")
    print(f"  Due Date: {inv1.due_date.strftime('%Y-%m-%d')}")
    
    inv2 = workflow.create_invoice(
        po_id=po2.id,
        gr_id=gr2.id,
        vendor_id="V002",
        vendor_name="Tech Solutions Inc.",
        line_items=items2,
        notes="Invoice for computer equipment"
    )
    print(f"✓ Created Invoice: {inv2.invoice_number} for {po2.po_number} - ${inv2.total_amount:.2f}")
    print(f"  Due Date: {inv2.due_date.strftime('%Y-%m-%d')}")
    
    inv3 = workflow.create_invoice(
        po_id=po3.id,
        gr_id=gr3.id,
        vendor_id="V003",
        vendor_name="Industrial Equipment Ltd.",
        line_items=items3,
        notes="Invoice for manufacturing equipment"
    )
    print(f"✓ Created Invoice: {inv3.invoice_number} for {po3.po_number} - ${inv3.total_amount:.2f}")
    print(f"  Due Date: {inv3.due_date.strftime('%Y-%m-%d')}")
    
    # Note: Cannot create invoice for PO4 yet - still pending approval
    print(f"✓ Skipping Invoice for {po4.po_number} - PO still pending approval")
    
    print("\n=== Processing Invoice Approvals ===")
    
    # Submit invoices for approval
    workflow.submit_invoice_for_approval(inv1.id)
    print(f"✓ {inv1.invoice_number} submitted for approval")
    
    workflow.submit_invoice_for_approval(inv2.id)
    print(f"✓ {inv2.invoice_number} submitted for approval")
    
    workflow.submit_invoice_for_approval(inv3.id)
    print(f"✓ {inv3.invoice_number} submitted for approval")
    
    # Approve invoices
    workflow.approve_invoice(inv1.id, "John Smith (Dept Manager)", "Verified against PO and GR")
    print(f"✓ {inv1.invoice_number} fully approved")
    
    workflow.approve_invoice(inv2.id, "John Smith (Dept Manager)", "Quantities and prices verified")
    workflow.approve_invoice(inv2.id, "Sarah Johnson (Finance Manager)", "Approved for payment")
    print(f"✓ {inv2.invoice_number} fully approved")
    
    # Leave inv3 with one pending approval
    workflow.approve_invoice(inv3.id, "John Smith (Dept Manager)", "Equipment received and verified")
    workflow.approve_invoice(inv3.id, "Sarah Johnson (Finance Manager)", "Capital budget confirmed")
    # Don't approve by CFO yet - leave it pending
    print(f"✓ {inv3.invoice_number} partially approved - awaiting CFO approval")
    
    print("\n=== Processing Payments ===")
    
    # Pay some invoices
    workflow.pay_invoice(inv1.id)
    print(f"✓ {inv1.invoice_number} marked as PAID")
    
    workflow.pay_invoice(inv2.id)
    print(f"✓ {inv2.invoice_number} marked as PAID")
    
    print(f"\n✓ {inv3.invoice_number} remains PENDING APPROVAL (awaiting CFO)")
    print(f"✓ {po4.po_number} remains PENDING APPROVAL (awaiting Finance Manager)")
    
    return workflow


if __name__ == "__main__":
    workflow = generate_sample_data()
    
    print("\n" + "="*60)
    print("Sample data generation completed successfully!")
    print("="*60)
