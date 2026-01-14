# Knowledge Graph Reasoning Guide

## Overview

The Knowledge Graph (KG) Reasoning system adds intelligent analysis and predictive capabilities to the P2P workflow application. It uses graph-based reasoning to detect fraud, assess vendor risks, recommend vendors, and predict potential issues.

## What is Knowledge Graph Reasoning?

Knowledge Graph Reasoning transforms your P2P data into a connected graph structure where:
- **Nodes** represent entities (Vendors, POs, Invoices, Approvers, Departments, Line Items)
- **Edges** represent relationships (supplies, requires_approval, validates, etc.)
- **Reasoning** derives new insights from these connections that aren't explicitly stored

## Key Features

### 1. Fraud Detection
Automatically detects suspicious patterns:
- **Unusual Invoice Amounts**: Invoices 3x higher than vendor's average
- **Split Invoicing**: Multiple small invoices to avoid approval thresholds
- **Blocked Document Patterns**: Vendors with multiple blocked documents

### 2. Vendor Risk Assessment
Calculates risk scores based on:
- Blocked documents (+20 points each)
- Quality rejections (+30 points each)
- Overdue invoices (+15 points each)
- Transaction volume (high volume with no issues = -10 points)

**Risk Levels:**
- LOW: Score < 30
- MEDIUM: Score 30-59
- HIGH: Score ≥ 60

### 3. Three-Way Match Validation
Validates PO → GR → Invoice relationships:
- Checks for missing references
- Detects amount variances (>5%)
- Verifies GR acceptance status

### 4. Approval Delay Prediction
Predicts which documents might face delays:
- High amounts requiring executive approval (+30)
- Multiple approvers required (+20)
- Vendor with blocked documents (+25)

### 5. Vendor Recommendations
Recommends vendors by category based on:
- Price competitiveness
- Risk score
- Quality performance
- Transaction history

### 6. Consolidation Opportunities
Identifies categories with 3+ vendors for potential consolidation.

## Installation

1. Install the required dependency:
```bash
pip install networkx==3.2.1
```

2. The KG reasoning module is already included in the project:
   - `kg_reasoning.py` - Core reasoning engine
   - `test_kg_reasoning.py` - Demo script

## Usage

### Basic Usage

```python
from workflow import P2PWorkflow
from sample_data import generate_sample_data
from kg_reasoning import P2PKnowledgeGraph

# Create workflow with data
workflow = generate_sample_data()

# Build knowledge graph
kg = P2PKnowledgeGraph()
kg.build_graph_from_workflow(workflow)

# Generate comprehensive report
report = kg.generate_comprehensive_report(workflow)

# Access specific insights
fraud_patterns = report['fraud_patterns']
vendor_risks = report['vendor_risks']
match_issues = report['three_way_match_issues']
delay_predictions = report['approval_delays']
consolidation = report['consolidation_opportunities']
```

### Running the Demo

```bash
python test_kg_reasoning.py
```

This generates a comprehensive analysis report with:
- Fraud detection results
- Vendor risk assessments
- Three-way match validation
- Approval delay predictions
- Vendor recommendations
- Consolidation opportunities
- Graph statistics

## API Reference

### P2PKnowledgeGraph Class

#### `__init__()`
Initialize a new knowledge graph.

#### `build_graph_from_workflow(workflow: P2PWorkflow)`
Build the knowledge graph from workflow data.

**Parameters:**
- `workflow`: P2PWorkflow instance with POs, GRs, and Invoices

#### `detect_fraud_patterns() -> List[Dict]`
Detect suspicious patterns indicating potential fraud.

**Returns:**
```python
[
    {
        'type': 'Unusual Invoice Amount',
        'severity': 'HIGH',
        'vendor': 'Vendor Name',
        'invoice_id': 'INV-123',
        'amount': 50000.0,
        'average': 15000.0,
        'reason': 'Invoice amount is 3.3x the average'
    },
    ...
]
```

#### `calculate_vendor_risk_scores() -> Dict[str, Dict]`
Calculate risk scores for all vendors.

**Returns:**
```python
{
    'V001': {
        'vendor_name': 'Acme Corp',
        'risk_score': 45,
        'risk_level': 'MEDIUM',
        'factors': ['Blocked documents: +20', 'Quality rejections: +30'],
        'transaction_count': 5
    },
    ...
}
```

#### `recommend_vendors(category: str, exclude_high_risk: bool = True) -> List[Dict]`
Recommend vendors for a product category.

**Parameters:**
- `category`: Product category (e.g., 'IT Equipment', 'Office Supplies')
- `exclude_high_risk`: Filter out high-risk vendors

**Returns:**
```python
[
    {
        'vendor_id': 'V001',
        'vendor_name': 'Tech Corp',
        'avg_price': 1250.00,
        'risk_score': 10,
        'risk_level': 'LOW',
        'quality_issues': 0,
        'blocked_count': 0,
        'transaction_count': 12
    },
    ...
]
```

#### `detect_three_way_match_issues() -> List[Dict]`
Detect issues in three-way matching.

**Returns:**
```python
[
    {
        'invoice_id': 'INV-123',
        'po_id': 'PO-456',
        'issue': 'Invoice amount $10,500 differs from PO $10,000',
        'severity': 'MEDIUM',
        'variance_pct': 5.0
    },
    ...
]
```

#### `predict_approval_delays() -> List[Dict]`
Predict which documents might face approval delays.

**Returns:**
```python
[
    {
        'document_id': 'PO-123',
        'document_type': 'PurchaseOrder',
        'amount': 25000.0,
        'delay_risk_score': 75,
        'risk_level': 'HIGH',
        'factors': [
            'High amount requiring executive approval',
            '3 approvers required',
            'Vendor has 2 blocked documents'
        ],
        'pending_approvers': 3
    },
    ...
]
```

#### `find_consolidation_opportunities() -> List[Dict]`
Find opportunities to consolidate vendors.

**Returns:**
```python
[
    {
        'category': 'IT Equipment',
        'vendor_count': 5,
        'total_spend': 125000.0,
        'vendors': {
            'V001': {'name': 'Tech Corp', 'spend': 50000.0, 'transaction_count': 10},
            ...
        },
        'recommendation': 'Consider consolidating 5 vendors for IT Equipment'
    },
    ...
]
```

#### `generate_comprehensive_report(workflow: P2PWorkflow) -> Dict`
Generate a comprehensive analysis report.

**Returns:**
```python
{
    'fraud_patterns': [...],
    'vendor_risks': {...},
    'three_way_match_issues': [...],
    'approval_delays': [...],
    'consolidation_opportunities': [...],
    'graph_stats': {
        'total_nodes': 150,
        'total_edges': 300,
        'total_vendors': 10,
        'total_pos': 50,
        'total_invoices': 45
    }
}
```

## Integration Examples

### 1. Real-time Fraud Monitoring

```python
def check_new_invoice(invoice: Invoice, workflow: P2PWorkflow):
    """Check new invoice for fraud patterns"""
    kg = P2PKnowledgeGraph()
    kg.build_graph_from_workflow(workflow)
    
    fraud_patterns = kg.detect_fraud_patterns()
    
    # Find patterns related to this invoice
    relevant_patterns = [
        p for p in fraud_patterns 
        if p.get('invoice_id') == invoice.id
    ]
    
    if relevant_patterns:
        # Auto-block suspicious invoice
        workflow.block_invoice(
            invoice.id, 
            f"Fraud detection: {relevant_patterns[0]['reason']}"
        )
        return False
    return True
```

### 2. Vendor Selection Assistant

```python
def suggest_best_vendor(category: str, workflow: P2PWorkflow):
    """Suggest the best vendor for a category"""
    kg = P2PKnowledgeGraph()
    kg.build_graph_from_workflow(workflow)
    
    recommendations = kg.recommend_vendors(category, exclude_high_risk=True)
    
    if recommendations:
        best_vendor = recommendations[0]
        print(f"Recommended: {best_vendor['vendor_name']}")
        print(f"Avg Price: ${best_vendor['avg_price']:.2f}")
        print(f"Risk: {best_vendor['risk_level']}")
        return best_vendor
    return None
```

### 3. Approval Route Optimization

```python
def optimize_approval_routing(po: PurchaseOrder, workflow: P2PWorkflow):
    """Optimize approval routing based on delay predictions"""
    kg = P2PKnowledgeGraph()
    kg.build_graph_from_workflow(workflow)
    
    predictions = kg.predict_approval_delays()
    
    # Find prediction for this PO
    po_prediction = next(
        (p for p in predictions if p['document_id'] == po.id),
        None
    )
    
    if po_prediction and po_prediction['delay_risk_score'] >= 60:
        # Send notification to approvers
        print(f"HIGH PRIORITY: {po.po_number} at risk of delays")
        print(f"Factors: {po_prediction['factors']}")
```

### 4. Automated Compliance Checking

```python
def check_compliance(workflow: P2PWorkflow):
    """Check for compliance issues"""
    kg = P2PKnowledgeGraph()
    kg.build_graph_from_workflow(workflow)
    
    issues = kg.detect_three_way_match_issues()
    
    high_severity = [i for i in issues if i['severity'] == 'HIGH']
    
    if high_severity:
        print(f"⚠️ {len(high_severity)} HIGH severity compliance issues found")
        for issue in high_severity:
            print(f"  - {issue['issue']}")
        return False
    return True
```

## Performance Considerations

- **Graph Building**: O(n) where n = total documents
- **Fraud Detection**: O(v × i) where v = vendors, i = invoices
- **Risk Calculation**: O(v × d) where v = vendors, d = documents
- **Recommendations**: O(c × v) where c = category items, v = vendors

For large datasets (>10,000 documents):
- Build graph incrementally
- Cache frequent queries
- Use graph database (Neo4j) instead of NetworkX

## Advanced Features

### Custom Reasoning Rules

You can add custom reasoning rules to detect specific patterns:

```python
def add_custom_rule(kg: P2PKnowledgeGraph):
    """Add a custom fraud detection rule"""
    # Example: Detect weekend transactions over $50k
    suspicious = []
    
    for node in kg.graph.nodes():
        if kg.graph.nodes[node].get('type') == 'PurchaseOrder':
            date = kg.graph.nodes[node].get('creation_date')
            amount = kg.graph.nodes[node].get('amount')
            
            if date.weekday() >= 5 and amount > 50000:
                suspicious.append({
                    'type': 'Weekend High-Value Transaction',
                    'po_id': node,
                    'amount': amount,
                    'severity': 'MEDIUM'
                })
    
    return suspicious
```

### Graph Visualization

```python
import matplotlib.pyplot as plt
import networkx as nx

def visualize_vendor_network(kg: P2PKnowledgeGraph, vendor_id: str):
    """Visualize a vendor's transaction network"""
    # Extract subgraph for vendor
    subgraph = nx.ego_graph(kg.graph, vendor_id, radius=2)
    
    # Draw graph
    pos = nx.spring_layout(subgraph)
    nx.draw(subgraph, pos, with_labels=True, node_color='lightblue')
    plt.show()
```

## Best Practices

1. **Regular Updates**: Rebuild the graph when data changes
2. **Threshold Tuning**: Adjust fraud detection thresholds based on your business
3. **Risk Scoring**: Customize risk factors based on industry requirements
4. **Monitoring**: Track false positives and adjust algorithms
5. **Performance**: For production, consider using Neo4j for scale

## Troubleshooting

**Issue**: Graph building is slow
- **Solution**: Reduce dataset size or use graph database

**Issue**: Too many false positives
- **Solution**: Adjust detection thresholds in `kg_reasoning.py`

**Issue**: Missing vendor recommendations
- **Solution**: Ensure sufficient transaction history exists

## Future Enhancements

- Machine learning for pattern recognition
- Temporal reasoning for time-series analysis
- Integration with external risk databases
- Real-time graph updates
- Advanced graph queries (SPARQL-like)
- Explanation generation for predictions

## Support

For questions or issues:
1. Check the test script: `test_kg_reasoning.py`
2. Review the implementation: `kg_reasoning.py`
3. See example integrations above

## License

Part of the P2P Workflow Prototype application.
