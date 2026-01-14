"""
Large sample data generator for P2P workflow demonstration
Generates 50+ records with various statuses
"""
from models import (
    LineItem, ApprovalPolicy, PaymentTerms, POStatus, GRStatus, InvoiceStatus
)
from workflow import P2PWorkflow
from datetime import datetime, timedelta
import random


# Sample data pools
VENDORS = [
    ("V001", "Office Supplies Co."),
    ("V002", "Tech Solutions Inc."),
    ("V003", "Industrial Equipment Ltd."),
    ("V004", "Business Consulting Group"),
    ("V005", "Furniture Warehouse"),
    ("V006", "Software Licensing Corp"),
    ("V007", "Cleaning Services Pro"),
    ("V008", "Marketing Agency Plus"),
    ("V009", "Legal Services LLC"),
    ("V010", "Logistics Partners"),
]

REQUESTERS = [
    ("Alice Williams", "Marketing"),
    ("Bob Chen", "IT"),
    ("Carlos Rodriguez", "Manufacturing"),
    ("Diana Lee", "Operations"),
    ("Emma Davis", "HR"),
    ("Frank Miller", "Sales"),
    ("Grace Taylor", "Finance"),
    ("Henry Wilson", "Legal"),
    ("Iris Johnson", "Procurement"),
    ("Jack Brown", "R&D"),
]

ITEMS_CATALOG = [
    ("OFF-001", "Premium Printer Paper", 25.99, "Office Supplies"),
    ("OFF-002", "Ballpoint Pens (Box)", 12.50, "Office Supplies"),
    ("OFF-003", "Sticky Notes", 3.99, "Office Supplies"),
    ("OFF-004", "File Folders (Pack)", 15.99, "Office Supplies"),
    ("IT-101", "Dell Latitude Laptop", 1299.99, "Computer Equipment"),
    ("IT-102", "27-inch Monitor", 349.99, "Computer Equipment"),
    ("IT-103", "Wireless Mouse & Keyboard", 79.99, "Peripherals"),
    ("IT-104", "USB-C Hub", 45.99, "Peripherals"),
    ("IT-105", "External SSD 1TB", 129.99, "Storage"),
    ("MFG-501", "Industrial 3D Printer", 8500.00, "Manufacturing"),
    ("MFG-502", "CNC Maintenance Kit", 2500.00, "Manufacturing"),
    ("MFG-503", "Safety Equipment Bundle", 150.00, "Safety"),
    ("MFG-504", "Tool Set Professional", 450.00, "Tools"),
    ("SVC-201", "Consulting Hours", 150.00, "Services"),
    ("SVC-202", "Training Materials", 500.00, "Services"),
    ("SVC-203", "Legal Review", 250.00, "Services"),
    ("FUR-301", "Office Desk", 599.99, "Furniture"),
    ("FUR-302", "Ergonomic Chair", 399.99, "Furniture"),
    ("FUR-303", "Conference Table", 1200.00, "Furniture"),
    ("SW-401", "Software License Annual", 999.00, "Software"),
]

APPROVERS = [
    "John Smith (Dept Manager)",
    "Sarah Johnson (Finance Manager)",
    "Michael Brown (CFO)"
]


def generate_large_sample_data() -> P2PWorkflow:
    """Generate 50+ purchase orders with complete workflow"""
    
    workflow = P2PWorkflow()
    
    # Setup approval policies
    print("\n=== Setting up Approval Policies ===")
    
    policy1 = ApprovalPolicy(
        name="Low Value Purchase Policy",
        description="For purchases up to $1,000 - requires department manager approval",
        min_amount=0.0,
        max_amount=1000.0,
        required_approvers=["John Smith (Dept Manager)"],
        approval_levels=1
    )
    workflow.add_approval_policy(policy1)
    
    policy2 = ApprovalPolicy(
        name="Medium Value Purchase Policy",
        description="For purchases $1,000 - $10,000 - requires department and finance approval",
        min_amount=1000.01,
        max_amount=10000.0,
        required_approvers=["John Smith (Dept Manager)", "Sarah Johnson (Finance Manager)"],
        approval_levels=2
    )
    workflow.add_approval_policy(policy2)
    
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
    print(f"✓ Added 3 approval policies")
    
    print("\n=== Generating 50 Purchase Orders ===")
    
    po_list = []
    
    # Spread POs across last 6 months for better trend visualization
    base_date = datetime.now()
    
    for i in range(50):
        # Randomly select vendor and requester
        vendor_id, vendor_name = random.choice(VENDORS)
        requester, department = random.choice(REQUESTERS)
        
        # Assign creation date spread across 6 months
        months_ago = random.randint(0, 5)
        days_offset = random.randint(0, 28)
        creation_date = base_date - timedelta(days=months_ago*30 + days_offset)
        
        # Generate 1-5 line items per PO
        num_items = random.randint(1, 5)
        line_items = []
        
        for _ in range(num_items):
            item_code, description, base_price, category = random.choice(ITEMS_CATALOG)
            quantity = random.randint(1, 20)
            # Add some price variation
            unit_price = round(base_price * random.uniform(0.9, 1.1), 2)
            
            line_items.append(LineItem(
                item_code=item_code,
                description=f"{description} ({category})",
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=0.10
            ))
        
        # Random payment terms
        payment_terms = random.choice(list(PaymentTerms))
        
        # Create PO
        po = workflow.create_purchase_order(
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            requester=requester,
            department=department,
            line_items=line_items,
            payment_terms=payment_terms,
            delivery_address=f"{department} Department, Building {random.choice(['A', 'B', 'C'])}",
            notes=f"Purchase request #{i+1}"
        )
        
        # Backdate the PO creation date for trend visualization
        po.creation_date = creation_date
        
        po_list.append(po)
    
    print(f"✓ Created {len(po_list)} purchase orders")
    
    print("\n=== Processing Purchase Orders ===")
    
    # Process POs with different outcomes
    approved_pos = []
    
    for idx, po in enumerate(po_list):
        workflow.submit_po_for_approval(po.id)
        
        # Determine approval outcome based on index for variety
        if idx < 35:  # First 35 get fully approved
            policy = workflow.get_applicable_policy(po.total_amount)
            if policy:
                for approver in policy.required_approvers:
                    workflow.approve_po(po.id, approver, f"Approved - {po.po_number}")
            approved_pos.append(po)
        elif idx < 40:  # Next 5 get partially approved (pending)
            policy = workflow.get_applicable_policy(po.total_amount)
            if policy and len(policy.required_approvers) > 0:
                # Approve only first approver
                workflow.approve_po(po.id, policy.required_approvers[0], "First level approved")
        elif idx < 43:  # Next 3 get rejected
            policy = workflow.get_applicable_policy(po.total_amount)
            if policy and len(policy.required_approvers) > 0:
                workflow.reject_po(po.id, policy.required_approvers[0], "Budget concerns")
        elif idx < 45:  # Next 2 get blocked
            workflow.submit_po_for_approval(po.id)
            workflow.block_po(po.id, "Vendor compliance issue - under investigation")
        # Last 5 remain in draft status
    
    print(f"✓ Processed {len(po_list)} POs:")
    print(f"  - Fully Approved: {len(approved_pos)}")
    print(f"  - Pending Approval: 5")
    print(f"  - Rejected: 3")
    print(f"  - Blocked: 2")
    print(f"  - Draft: 5")
    
    print("\n=== Creating Goods Receipts ===")
    
    gr_list = []
    
    # Create GRs for 30 of the approved POs
    for idx, po in enumerate(approved_pos[:30]):
        receivers = [
            "Warehouse - Tom Anderson",
            "IT Dept - Bob Chen",
            "Manufacturing - Carlos Rodriguez",
            "Operations - Diana Lee"
        ]
        
        gr = workflow.create_goods_receipt(
            po_id=po.id,
            received_by=random.choice(receivers),
            line_items=po.line_items,
            notes=f"Goods received for {po.po_number}"
        )
        
        if gr:
            gr_list.append(gr)
    
    print(f"✓ Created {len(gr_list)} goods receipts")
    
    print("\n=== Performing Quality Checks ===")
    
    quality_checkers = [
        "Quality Team - Emma Davis",
        "QA - Frank Miller",
        "Inspector - Grace Taylor"
    ]
    
    accepted_grs = []
    
    # Perform quality checks - 25 pass, 3 fail, 2 blocked
    for idx, gr in enumerate(gr_list):
        if idx < 25:
            workflow.perform_quality_check(gr.id, random.choice(quality_checkers), True)
            accepted_grs.append(gr)
        elif idx < 28:
            workflow.perform_quality_check(gr.id, random.choice(quality_checkers), False)
        elif idx < 30:
            workflow.block_gr(gr.id, "Quantity discrepancy - investigation required")
    
    print(f"✓ Quality checks completed:")
    print(f"  - Accepted: {len(accepted_grs)}")
    print(f"  - Rejected: 3")
    print(f"  - Blocked: 2")
    
    print("\n=== Creating Invoices ===")
    
    invoice_list = []
    
    # Create invoices for all accepted GRs
    for gr in accepted_grs:
        po = workflow.purchase_orders.get(gr.po_id)
        if po:
            invoice = workflow.create_invoice(
                po_id=po.id,
                gr_id=gr.id,
                vendor_id=po.vendor_id,
                vendor_name=po.vendor_name,
                line_items=gr.line_items,
                notes=f"Invoice for {po.po_number}"
            )
            if invoice:
                invoice_list.append(invoice)
    
    print(f"✓ Created {len(invoice_list)} invoices")
    
    print("\n=== Processing Invoice Approvals ===")
    
    # Submit all invoices
    for invoice in invoice_list:
        workflow.submit_invoice_for_approval(invoice.id)
    
    # Process invoices with different outcomes
    for idx, invoice in enumerate(invoice_list):
        if idx < 15:  # First 15 fully approved and paid
            policy = workflow.get_applicable_policy(invoice.total_amount)
            if policy:
                for approver in policy.required_approvers:
                    workflow.approve_invoice(invoice.id, approver, f"Approved - {invoice.invoice_number}")
            workflow.pay_invoice(invoice.id)
        elif idx < 20:  # Next 5 approved but not paid
            policy = workflow.get_applicable_policy(invoice.total_amount)
            if policy:
                for approver in policy.required_approvers:
                    workflow.approve_invoice(invoice.id, approver, "Approved for payment")
        elif idx < 23:  # Next 3 partially approved (pending)
            policy = workflow.get_applicable_policy(invoice.total_amount)
            if policy and len(policy.required_approvers) > 0:
                workflow.approve_invoice(invoice.id, policy.required_approvers[0], "First level approved")
        elif idx < 24:  # 1 blocked - Pricing discrepancy
            workflow.block_invoice(invoice.id, "Pricing discrepancy - vendor contacted")
        elif idx < 25:  # 1 blocked - Three-way match failure
            workflow.block_invoice(invoice.id, "Three-way match failure - quantity mismatch between PO, GR, and invoice")
        elif idx < 26:  # 1 blocked - Missing documentation
            workflow.block_invoice(invoice.id, "Missing documentation - awaiting signed delivery receipt from vendor")
        # Rest remain in draft or pending
    
    print(f"✓ Processed {len(invoice_list)} invoices:")
    print(f"  - Paid: 15")
    print(f"  - Approved (Pending Payment): 5")
    print(f"  - Pending Approval: 3")
    print(f"  - Blocked: 3 (Pricing, Three-way match, Missing docs)")
    print(f"  - Draft: {len(invoice_list) - 26}")
    
    # Summary
    print("\n" + "="*80)
    print("LARGE SAMPLE DATA GENERATION COMPLETE")
    print("="*80)
    
    stats = workflow.get_statistics()
    print(f"\nTotal Documents Created:")
    print(f"  Purchase Orders: {stats['total_pos']}")
    print(f"  Goods Receipts: {stats['total_grs']}")
    print(f"  Invoices: {stats['total_invoices']}")
    print(f"\nTotal Spend: ${stats['total_spend']:,.2f}")
    
    return workflow


if __name__ == "__main__":
    workflow = generate_large_sample_data()
