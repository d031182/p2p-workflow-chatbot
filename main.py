"""
Main application with CLI interface for P2P workflow prototype
"""
from workflow import P2PWorkflow
from sample_data import generate_sample_data
from models import POStatus, GRStatus, InvoiceStatus
from datetime import datetime


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_po_details(po):
    """Print purchase order details"""
    print(f"\nPurchase Order: {po.po_number}")
    print(f"  Vendor: {po.vendor_name} (ID: {po.vendor_id})")
    print(f"  Requester: {po.requester} ({po.department})")
    print(f"  Status: {po.status.value}")
    print(f"  Creation Date: {po.creation_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Payment Terms: {po.payment_terms.value}")
    print(f"  Delivery Address: {po.delivery_address}")
    
    print(f"\n  Line Items:")
    for item in po.line_items:
        print(f"    - {item.description}")
        print(f"      Code: {item.item_code} | Qty: {item.quantity} | Unit Price: ${item.unit_price:.2f}")
        print(f"      Subtotal: ${item.subtotal:.2f} | Tax: ${item.tax_amount:.2f} | Total: ${item.total:.2f}")
    
    print(f"\n  Financial Summary:")
    print(f"    Subtotal: ${po.subtotal:.2f}")
    print(f"    Tax Total: ${po.tax_total:.2f}")
    print(f"    Total Amount: ${po.total_amount:.2f}")
    
    if po.approvals:
        print(f"\n  Approval History:")
        for approval in po.approvals:
            print(f"    - {approval.approver}: {approval.status}")
            if approval.comments:
                print(f"      Comment: {approval.comments}")
            print(f"      Timestamp: {approval.timestamp.strftime('%Y-%m-%d %H:%M')}")
    
    if po.notes:
        print(f"\n  Notes: {po.notes}")


def print_gr_details(gr):
    """Print goods receipt details"""
    print(f"\nGoods Receipt: {gr.gr_number}")
    print(f"  Related PO: {gr.po_number}")
    print(f"  Status: {gr.status.value}")
    print(f"  Receipt Date: {gr.receipt_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Received By: {gr.received_by}")
    
    print(f"\n  Line Items:")
    for item in gr.line_items:
        print(f"    - {item.description}")
        print(f"      Code: {item.item_code} | Qty: {item.quantity} | Total: ${item.total:.2f}")
    
    print(f"\n  Total Amount: ${gr.total_amount:.2f}")
    
    if gr.quality_checked:
        print(f"\n  Quality Check:")
        print(f"    Performed by: {gr.quality_checker}")
        print(f"    Date: {gr.quality_check_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"    Result: {'PASSED' if gr.status == GRStatus.ACCEPTED else 'FAILED'}")
    
    if gr.notes:
        print(f"\n  Notes: {gr.notes}")


def print_invoice_details(invoice):
    """Print invoice details"""
    print(f"\nInvoice: {invoice.invoice_number}")
    print(f"  Vendor: {invoice.vendor_name} (ID: {invoice.vendor_id})")
    print(f"  Related PO: {invoice.po_number}")
    print(f"  Related GR: {invoice.gr_number}")
    print(f"  Status: {invoice.status.value}")
    print(f"  Invoice Date: {invoice.invoice_date.strftime('%Y-%m-%d')}")
    print(f"  Due Date: {invoice.due_date.strftime('%Y-%m-%d')}")
    print(f"  Payment Terms: {invoice.payment_terms.value}")
    
    if invoice.payment_date:
        print(f"  Payment Date: {invoice.payment_date.strftime('%Y-%m-%d')}")
    
    print(f"\n  Line Items:")
    for item in invoice.line_items:
        print(f"    - {item.description}")
        print(f"      Code: {item.item_code} | Qty: {item.quantity} | Unit Price: ${item.unit_price:.2f}")
        print(f"      Subtotal: ${item.subtotal:.2f} | Tax: ${item.tax_amount:.2f} | Total: ${item.total:.2f}")
    
    print(f"\n  Financial Summary:")
    print(f"    Subtotal: ${invoice.subtotal:.2f}")
    print(f"    Tax Total: ${invoice.tax_total:.2f}")
    print(f"    Total Amount: ${invoice.total_amount:.2f}")
    
    if invoice.approvals:
        print(f"\n  Approval History:")
        for approval in invoice.approvals:
            print(f"    - {approval.approver}: {approval.status}")
            if approval.comments:
                print(f"      Comment: {approval.comments}")
            print(f"      Timestamp: {approval.timestamp.strftime('%Y-%m-%d %H:%M')}")
    
    if invoice.notes:
        print(f"\n  Notes: {invoice.notes}")


def display_all_purchase_orders(workflow: P2PWorkflow):
    """Display all purchase orders"""
    print_header("ALL PURCHASE ORDERS")
    
    if not workflow.purchase_orders:
        print("\nNo purchase orders found.")
        return
    
    for po in workflow.purchase_orders.values():
        print_po_details(po)
        print("-" * 80)


def display_all_goods_receipts(workflow: P2PWorkflow):
    """Display all goods receipts"""
    print_header("ALL GOODS RECEIPTS")
    
    if not workflow.goods_receipts:
        print("\nNo goods receipts found.")
        return
    
    for gr in workflow.goods_receipts.values():
        print_gr_details(gr)
        print("-" * 80)


def display_all_invoices(workflow: P2PWorkflow):
    """Display all invoices"""
    print_header("ALL INVOICES")
    
    if not workflow.invoices:
        print("\nNo invoices found.")
        return
    
    for invoice in workflow.invoices.values():
        print_invoice_details(invoice)
        print("-" * 80)


def display_approval_policies(workflow: P2PWorkflow):
    """Display approval policies"""
    print_header("APPROVAL POLICIES")
    
    if not workflow.approval_policies:
        print("\nNo approval policies configured.")
        return
    
    for policy in workflow.approval_policies:
        print(f"\n{policy.name}")
        print(f"  Description: {policy.description}")
        print(f"  Amount Range: ${policy.min_amount:.2f} - ${policy.max_amount:.2f}")
        print(f"  Approval Levels: {policy.approval_levels}")
        print(f"  Required Approvers:")
        for approver in policy.required_approvers:
            print(f"    - {approver}")


def display_pending_approvals(workflow: P2PWorkflow):
    """Display pending approvals"""
    print_header("PENDING APPROVALS")
    
    pending = workflow.get_all_pending_approvals()
    
    if pending['purchase_orders']:
        print("\nPending Purchase Orders:")
        for po in pending['purchase_orders']:
            print(f"\n  PO: {po.po_number} - ${po.total_amount:.2f}")
            print(f"  Requester: {po.requester} ({po.department})")
            print(f"  Vendor: {po.vendor_name}")
            print(f"  Pending Approvals:")
            for approval in po.approvals:
                if approval.status == "Pending":
                    print(f"    - {approval.approver}: {approval.status}")
    else:
        print("\nNo pending purchase order approvals.")
    
    if pending['invoices']:
        print("\nPending Invoices:")
        for inv in pending['invoices']:
            print(f"\n  Invoice: {inv.invoice_number} - ${inv.total_amount:.2f}")
            print(f"  Vendor: {inv.vendor_name}")
            print(f"  Related PO: {inv.po_number}")
            print(f"  Pending Approvals:")
            for approval in inv.approvals:
                if approval.status == "Pending":
                    print(f"    - {approval.approver}: {approval.status}")
    else:
        print("\nNo pending invoice approvals.")


def display_po_summary(workflow: P2PWorkflow, po_id: str):
    """Display complete summary for a PO"""
    print_header(f"PURCHASE ORDER SUMMARY: {po_id}")
    
    summary = workflow.get_po_summary(po_id)
    
    if not summary:
        print(f"\nPurchase order {po_id} not found.")
        return
    
    print_po_details(summary['purchase_order'])
    
    if summary['goods_receipts']:
        print("\n" + "-" * 80)
        print("RELATED GOODS RECEIPTS:")
        for gr in summary['goods_receipts']:
            print_gr_details(gr)
    
    if summary['invoices']:
        print("\n" + "-" * 80)
        print("RELATED INVOICES:")
        for inv in summary['invoices']:
            print_invoice_details(inv)
    
    print("\n" + "-" * 80)
    print("FINANCIAL SUMMARY:")
    print(f"  PO Total Amount: ${summary['purchase_order'].total_amount:.2f}")
    print(f"  Total Received: ${summary['total_received']:.2f}")
    print(f"  Total Invoiced: ${summary['total_invoiced']:.2f}")
    print(f"  Total Paid: ${summary['total_paid']:.2f}")
    print(f"  Outstanding: ${summary['total_invoiced'] - summary['total_paid']:.2f}")


def display_blocked_documents(workflow: P2PWorkflow):
    """Display blocked documents"""
    print_header("BLOCKED DOCUMENTS")
    
    blocked = workflow.get_blocked_documents()
    
    if blocked['purchase_orders']:
        print("\nBlocked Purchase Orders:")
        for po in blocked['purchase_orders']:
            print(f"\n  PO: {po.po_number} - ${po.total_amount:.2f}")
            print(f"  Requester: {po.requester} ({po.department})")
            print(f"  Vendor: {po.vendor_name}")
            print(f"  ⚠ BLOCKED REASON: {po.blocked_reason}")
    else:
        print("\nNo blocked purchase orders.")
    
    if blocked['goods_receipts']:
        print("\nBlocked Goods Receipts:")
        for gr in blocked['goods_receipts']:
            print(f"\n  GR: {gr.gr_number}")
            print(f"  Related PO: {gr.po_number}")
            print(f"  Received By: {gr.received_by}")
            print(f"  ⚠ BLOCKED REASON: {gr.blocked_reason}")
    else:
        print("\nNo blocked goods receipts.")
    
    if blocked['invoices']:
        print("\nBlocked Invoices:")
        for inv in blocked['invoices']:
            print(f"\n  Invoice: {inv.invoice_number} - ${inv.total_amount:.2f}")
            print(f"  Vendor: {inv.vendor_name}")
            print(f"  Related PO: {inv.po_number}")
            print(f"  ⚠ BLOCKED REASON: {inv.blocked_reason}")
    else:
        print("\nNo blocked invoices.")


def display_statistics(workflow: P2PWorkflow):
    """Display workflow statistics"""
    print_header("WORKFLOW STATISTICS")
    
    stats = workflow.get_statistics()
    
    print("\nPurchase Orders:")
    print(f"  Total: {stats['total_pos']}")
    print(f"  Approved: {stats['approved_pos']}")
    print(f"  Pending Approval: {stats['pending_pos']}")
    print(f"  Blocked: {stats['blocked_pos']}")
    
    print("\nGoods Receipts:")
    print(f"  Total: {stats['total_grs']}")
    print(f"  Accepted: {stats['accepted_grs']}")
    print(f"  Blocked: {stats['blocked_grs']}")
    
    print("\nInvoices:")
    print(f"  Total: {stats['total_invoices']}")
    print(f"  Paid: {stats['paid_invoices']}")
    print(f"  Overdue: {stats['overdue_invoices']}")
    print(f"  Blocked: {stats['blocked_invoices']}")
    
    print("\nFinancial Summary:")
    print(f"  Total Spend (Paid Invoices): ${stats['total_spend']:.2f}")


def display_menu():
    """Display main menu"""
    print("\n" + "=" * 80)
    print("P2P WORKFLOW PROTOTYPE - MAIN MENU")
    print("=" * 80)
    print("\n1.  View All Purchase Orders")
    print("2.  View All Goods Receipts")
    print("3.  View All Invoices")
    print("4.  View Approval Policies")
    print("5.  View Pending Approvals")
    print("6.  View Blocked Documents")
    print("7.  View PO Summary (with related documents)")
    print("8.  View Workflow Statistics")
    print("9.  Regenerate Sample Data")
    print("10. Exit")
    print("\n" + "=" * 80)


def main():
    """Main application entry point"""
    print_header("PURCHASE-TO-PAY (P2P) WORKFLOW PROTOTYPE")
    print("\nWelcome to the P2P Workflow Prototype Application!")
    print("This application demonstrates a complete purchase-to-pay business process")
    print("including Purchase Orders, Goods Receipts, Invoices, and Approval Workflows.")
    
    print("\nGenerating sample data...")
    workflow = generate_sample_data()
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-10): ").strip()
        
        if choice == '1':
            display_all_purchase_orders(workflow)
        elif choice == '2':
            display_all_goods_receipts(workflow)
        elif choice == '3':
            display_all_invoices(workflow)
        elif choice == '4':
            display_approval_policies(workflow)
        elif choice == '5':
            display_pending_approvals(workflow)
        elif choice == '6':
            display_blocked_documents(workflow)
        elif choice == '7':
            print("\nAvailable Purchase Orders:")
            for po_id, po in workflow.purchase_orders.items():
                print(f"  - {po.po_number} (ID: {po_id})")
            po_input = input("\nEnter PO ID or PO Number: ").strip()
            # Find PO by ID or number
            found_po = None
            for po_id, po in workflow.purchase_orders.items():
                if po_id == po_input or po.po_number == po_input:
                    found_po = po_id
                    break
            if found_po:
                display_po_summary(workflow, found_po)
            else:
                print(f"\nPurchase order '{po_input}' not found.")
        elif choice == '8':
            display_statistics(workflow)
        elif choice == '9':
            print("\nRegenerating sample data...")
            workflow = generate_sample_data()
        elif choice == '10':
            print_header("THANK YOU")
            print("\nThank you for using the P2P Workflow Prototype!")
            print("Exiting application...")
            break
        else:
            print("\n⚠ Invalid choice. Please enter a number between 1 and 10.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
