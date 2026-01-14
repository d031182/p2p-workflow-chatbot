# Document Status Guide

This guide explains the processing statuses for all document types in the P2P workflow.

## Purchase Order Status Lifecycle

```
DRAFT
  ↓ (Submit for Approval)
PENDING APPROVAL
  ↓ (All approvers approve)
APPROVED
  ↓ (Goods Receipt created)
IN PROGRESS
  ↓ (All Goods Receipts accepted)
COMPLETED
```

### Status Definitions

| Status | Description | What It Means |
|--------|-------------|---------------|
| **Draft** | Initial state | PO created but not submitted for approval |
| **Pending Approval** | Awaiting approval | PO submitted, waiting for required approvers |
| **Approved** | Ready for fulfillment | All approvals received, can proceed to ordering |
| **Rejected** | Denied | At least one approver rejected the PO |
| **In Progress** | Order fulfillment | Goods receipt created, items being received |
| **Completed** | Fully received | All items received and quality checked |
| **Cancelled** | Voided | PO cancelled before completion |
| **Blocked** | Processing halted | Issue prevents processing (e.g., vendor issues, budget hold) |

## Goods Receipt Status Lifecycle

```
DRAFT
  ↓ (Mark as received)
RECEIVED
  ↓ (Perform quality check)
QUALITY CHECK
  ↓ (Pass/Fail)
ACCEPTED or REJECTED
```

### Status Definitions

| Status | Description | What It Means |
|--------|-------------|---------------|
| **Draft** | Initial state | GR created but goods not marked as received |
| **Received** | Delivery confirmed | Goods physically received, awaiting quality check |
| **Quality Check** | Under inspection | Quality check in progress |
| **Accepted** | Quality approved | Goods passed quality check, ready for invoice |
| **Rejected** | Quality failed | Goods failed quality check, cannot invoice |
| **Blocked** | Processing halted | Issue prevents processing (e.g., discrepancies, damage) |

## Invoice Status Lifecycle

```
DRAFT
  ↓ (Submit for Approval)
PENDING APPROVAL
  ↓ (All approvers approve)
APPROVED
  ↓ (Process payment)
PAID
```

### Status Definitions

| Status | Description | What It Means |
|--------|-------------|---------------|
| **Draft** | Initial state | Invoice created but not submitted |
| **Pending Approval** | Awaiting approval | Invoice submitted, waiting for required approvers |
| **Approved** | Ready for payment | All approvals received, can proceed to payment |
| **Rejected** | Denied | At least one approver rejected the invoice |
| **Paid** | Payment completed | Invoice paid, transaction complete |
| **Overdue** | Past due date | Invoice approved but not paid by due date |
| **Blocked** | Processing halted | Issue prevents processing (e.g., pricing disputes, missing info) |

## Complete P2P Process Flow

```
1. CREATE PURCHASE ORDER → Status: Draft
   ↓
2. SUBMIT FOR APPROVAL → Status: Pending Approval
   ↓
3. APPROVALS COMPLETE → Status: Approved
   ↓
4. CREATE GOODS RECEIPT → PO Status: In Progress, GR Status: Draft
   ↓
5. MARK AS RECEIVED → GR Status: Received
   ↓
6. QUALITY CHECK PASS → GR Status: Accepted, PO Status: Completed
   ↓
7. CREATE INVOICE → Invoice Status: Draft
   ↓
8. SUBMIT FOR APPROVAL → Invoice Status: Pending Approval
   ↓
9. APPROVALS COMPLETE → Invoice Status: Approved
   ↓
10. PROCESS PAYMENT → Invoice Status: Paid
```

## Status Indicators in the Application

When viewing documents in the application, you'll see:

### Purchase Order Example
```
Status: Completed
```
This means: PO approved → Goods received → Quality checked → Ready for invoicing

### Goods Receipt Example
```
Status: Accepted
```
This means: Goods received → Quality check passed → Can create invoice

### Invoice Example
```
Status: Paid
Payment Date: 2026-01-13
```
This means: Invoice approved → Payment processed → Transaction complete

OR

```
Status: Approved
Due Date: 2026-04-13
```
This means: Invoice approved → Waiting for payment → Still within payment terms

## Business Rules

1. **PO → GR**: Can only create GR for **Approved** POs
2. **GR → Quality**: GR must be **Received** before quality check
3. **GR → Invoice**: Can only create invoice for **Accepted** GRs
4. **Invoice → Payment**: Can only pay **Approved** invoices
5. **Overdue Detection**: System automatically marks **Approved** invoices as **Overdue** when past due date

## Viewing Status in the Application

Use these menu options to view documents by status:

- **Option 1**: View All Purchase Orders (shows each PO's status)
- **Option 2**: View All Goods Receipts (shows each GR's status)
- **Option 3**: View All Invoices (shows each invoice's status)
- **Option 5**: View Pending Approvals (shows documents awaiting approval)
- **Option 6**: View Blocked Documents (shows documents with processing issues)
- **Option 8**: View Workflow Statistics (shows counts by status including blocked)

## Status Transitions

### Automatic Transitions
- PO: Draft → Approved (when no approval policy applies)
- PO: Approved → In Progress (when first GR is created)
- PO: In Progress → Completed (when all GRs are accepted)
- GR: Draft → Received (when marked as received)
- Invoice: Draft → Approved (when no approval policy applies)
- Invoice: Approved → Overdue (system checks based on due date)

### Manual Transitions (require action)
- PO: Draft → Pending Approval (submit for approval)
- PO: Pending → Approved (approvers approve)
- PO: Pending → Rejected (approver rejects)
- GR: Received → Accepted/Rejected (quality check result)
- Invoice: Draft → Pending Approval (submit for approval)
- Invoice: Pending → Approved (approvers approve)
- Invoice: Approved → Paid (payment processing)

### Blocked Status (Manual - when issues occur)
- PO: Any status → Blocked (when vendor issues, budget holds, or other problems occur)
- GR: Any status → Blocked (when discrepancies, damages, or quality issues arise)
- Invoice: Any status → Blocked (when pricing disputes, missing information, or payment issues occur)
- Invoice: Blocked → Draft (when issue is resolved and unblocked)

## Common Blocking Scenarios

### Purchase Orders May Be Blocked Due To:
- Vendor issues (bankruptcy, suspension, compliance problems)
- Budget freeze or reallocation
- Regulatory compliance issues
- Contract disputes
- Missing required documentation

### Goods Receipts May Be Blocked Due To:
- Quantity discrepancies (over/under delivery)
- Damaged goods exceeding acceptable threshold
- Missing documentation (packing slip, certificates)
- Wrong items delivered
- Serial number mismatches

### Invoices May Be Blocked Due To:
- Pricing discrepancies between PO and invoice
- Missing or incorrect purchase order reference
- Tax calculation errors
- Payment terms mismatch
- Duplicate invoice detection
- Missing approval signatures
- Bank account information issues
