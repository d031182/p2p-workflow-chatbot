# Purchase-to-Pay (P2P) Workflow Prototype

A comprehensive Python application demonstrating a complete Purchase-to-Pay business process including Purchase Orders, Goods Receipts, Invoices, Payment Terms, and Approval Policies.

## Features

### Core Functionality
- **Purchase Order Management**: Create, approve, and track purchase orders
- **Goods Receipt Processing**: Record and validate received goods/services
- **Invoice Management**: Create, approve, and process vendor invoices
- **Approval Workflows**: Multi-level approval policies based on transaction amounts
- **Payment Terms**: Support for various payment terms (Net 30/60/90, Immediate, Due on Receipt)
- **Complete Audit Trail**: Track all approvals and status changes with timestamps

### Business Logic
- Automatic approval routing based on configurable policies
- Multi-level approval requirements (Department, Finance, Executive)
- Three-way matching: PO → GR → Invoice
- Quality check workflows for received goods
- Payment tracking and overdue invoice detection
- Comprehensive financial reporting

## Project Structure

```
steel_thread/
├── models.py              # Data models (PO, GR, Invoice, Approval policies)
├── workflow.py            # Business logic and workflow management
├── sample_data.py         # Sample data generator
├── main.py               # CLI application interface
├── web_app.py            # Flask web application
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates for web UI
├── static/css/           # CSS stylesheets
└── README.md             # This file
```

## Installation

### Prerequisites
- Python 3.7 or higher

### Setup
1. Navigate to the project directory:
   ```bash
   cd steel_thread
   ```

2. Install dependencies (for web application):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Web Application (Recommended)

```bash
python web_app.py
```

Then open your browser and navigate to: **http://localhost:5000**

The web application provides a modern UI with interactive dashboard, document viewing, and real-time status tracking.

### Running the CLI Application

```bash
python main.py
```

### CLI Menu Options

1. **View All Purchase Orders** - Display all POs with complete details
2. **View All Goods Receipts** - Display all GRs with receipt information
3. **View All Invoices** - Display all invoices with payment status
4. **View Approval Policies** - Show configured approval policies
5. **View Pending Approvals** - List all documents awaiting approval
6. **View PO Summary** - Complete view of PO with related GR and invoices
7. **View Workflow Statistics** - Overall system statistics and financial summary
8. **Regenerate Sample Data** - Reset and create new sample data
9. **Exit** - Close the application

## Sample Data

The application automatically generates comprehensive sample data including:

### Approval Policies
- **Low Value** ($0 - $1,000): Single department manager approval
- **Medium Value** ($1,000 - $10,000): Department + Finance approval
- **High Value** (>$10,000): Department + Finance + Executive approval

### Sample Transactions
1. **Office Supplies** ($412.17) - Low value transaction
   - Paper, pens, sticky notes
   - Net 30 payment terms
   - Single approval required

2. **Computer Equipment** ($5,709.18) - Medium value transaction
   - Laptops, monitors, peripherals
   - Net 60 payment terms
   - Two-level approval required

3. **Manufacturing Equipment** ($22,165.00) - High value transaction
   - Industrial 3D printers, CNC maintenance, safety equipment
   - Net 90 payment terms
   - Three-level approval required

4. **Consulting Services** ($7,150.00) - Medium value transaction
   - Business consulting hours and training materials
   - Net 30 payment terms
   - Two-level approval required

## Data Models

### PurchaseOrder
- Vendor information
- Line items with quantities, prices, and tax
- Status tracking (Draft, Pending Approval, Approved, etc.)
- Payment terms
- Approval records

### GoodsReceipt
- Reference to Purchase Order
- Receipt date and received by information
- Line items received
- Quality check status and results

### Invoice
- Reference to PO and GR
- Vendor information
- Line items with financial details
- Due date calculation based on payment terms
- Approval workflow
- Payment tracking

### ApprovalPolicy
- Amount thresholds
- Required approvers list
- Approval levels configuration

## Workflow Process

```
1. Create Purchase Order
   ↓
2. Submit for Approval (auto-routed based on amount)
   ↓
3. Multi-level Approvals (Department → Finance → Executive)
   ↓
4. Create Goods Receipt (upon delivery)
   ↓
5. Perform Quality Check
   ↓
6. Create Invoice (vendor submits)
   ↓
7. Submit Invoice for Approval
   ↓
8. Process Payment
```

## Key Features Demonstrated

### 1. Approval Policies
- Dynamic policy matching based on transaction amount
- Configurable approval chains
- Complete approval audit trail

### 2. Three-Way Matching
- PO → GR → Invoice validation
- Prevents payment without proper receipts
- Ensures goods/services validation before payment

### 3. Payment Terms
- Multiple payment term options
- Automatic due date calculation
- Overdue invoice tracking

### 4. Financial Tracking
- Subtotal, tax, and total calculations
- Payment status monitoring
- Comprehensive financial reporting

### 5. Status Management
- Purchase Order: Draft → Pending → Approved → In Progress → Completed
- Goods Receipt: Draft → Received → Quality Check → Accepted
- Invoice: Draft → Pending → Approved → Paid

## Extending the Application

### Adding New Approval Policies
```python
policy = ApprovalPolicy(
    name="Custom Policy",
    description="Policy description",
    min_amount=0.0,
    max_amount=1000.0,
    required_approvers=["Approver Name"],
    approval_levels=1
)
workflow.add_approval_policy(policy)
```

### Creating Custom Purchase Orders
```python
items = [
    LineItem(
        item_code="ITEM-001",
        description="Product description",
        quantity=10,
        unit_price=99.99,
        tax_rate=0.10
    )
]

po = workflow.create_purchase_order(
    vendor_id="V001",
    vendor_name="Vendor Name",
    requester="Employee Name",
    department="Department",
    line_items=items,
    payment_terms=PaymentTerms.NET_30
)
```

## Business Rules Implemented

1. **Approval Requirements**: POs and invoices must be approved before proceeding
2. **GR Prerequisites**: Can only create GR for approved POs
3. **Quality Gates**: GR must pass quality check before invoice creation
4. **Invoice Validation**: Invoice requires both PO and accepted GR
5. **Payment Authorization**: Only approved invoices can be paid
6. **Status Progression**: Documents follow defined status workflows

## License

This is a prototype application for demonstration purposes.

## Author

Created with Cline AI Assistant
Date: January 2026
