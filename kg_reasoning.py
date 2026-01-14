"""
Knowledge Graph Reasoning for Purchase-to-Pay Application
Implements intelligent analysis, fraud detection, and recommendations using graph-based reasoning
"""
import networkx as nx
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from models import (
    PurchaseOrder, GoodsReceipt, Invoice, LineItem,
    POStatus, GRStatus, InvoiceStatus, ApprovalPolicy
)
from workflow import P2PWorkflow


class P2PKnowledgeGraph:
    """Knowledge Graph for P2P workflow with reasoning capabilities"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entity_properties = {}
        self.reasoning_rules = []
        
    def build_graph_from_workflow(self, workflow: P2PWorkflow):
        """Convert workflow data into a knowledge graph"""
        print("Building knowledge graph from workflow data...")
        
        # Add vendors
        vendors = set()
        for po in workflow.purchase_orders.values():
            vendors.add((po.vendor_id, po.vendor_name))
        
        for vendor_id, vendor_name in vendors:
            self.add_vendor(vendor_id, vendor_name)
        
        # Add departments
        departments = set(po.department for po in workflow.purchase_orders.values())
        for dept in departments:
            self.add_department(dept)
        
        # Add approvers
        approvers = set()
        for po in workflow.purchase_orders.values():
            for approval in po.approvals:
                approvers.add(approval.approver)
        for invoice in workflow.invoices.values():
            for approval in invoice.approvals:
                approvers.add(approval.approver)
        
        for approver in approvers:
            self.add_approver(approver)
        
        # Add purchase orders with relationships
        for po in workflow.purchase_orders.values():
            self.add_purchase_order(po)
        
        # Add goods receipts
        for gr in workflow.goods_receipts.values():
            self.add_goods_receipt(gr, workflow)
        
        # Add invoices
        for invoice in workflow.invoices.values():
            self.add_invoice(invoice, workflow)
        
        # Add product categories (inferred from line items)
        self._add_product_categories(workflow)
        
        print(f"Knowledge graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        
    def add_vendor(self, vendor_id: str, vendor_name: str):
        """Add vendor node to graph"""
        self.graph.add_node(
            vendor_id,
            type='Vendor',
            name=vendor_name,
            risk_score=0,
            total_spend=0,
            transaction_count=0
        )
        
    def add_department(self, department: str):
        """Add department node to graph"""
        self.graph.add_node(
            f"DEPT_{department}",
            type='Department',
            name=department,
            total_spend=0
        )
        
    def add_approver(self, approver: str):
        """Add approver node to graph"""
        self.graph.add_node(
            f"APPROVER_{approver}",
            type='Approver',
            name=approver,
            approval_count=0,
            avg_approval_time=0
        )
        
    def add_purchase_order(self, po: PurchaseOrder):
        """Add purchase order and its relationships"""
        self.graph.add_node(
            po.id,
            type='PurchaseOrder',
            amount=po.total_amount,
            status=po.status.value,
            creation_date=po.creation_date,
            requester=po.requester,
            blocked=po.status == POStatus.BLOCKED,
            blocked_reason=po.blocked_reason
        )
        
        # Vendor relationship
        self.graph.add_edge(po.id, po.vendor_id, relation='FROM_VENDOR')
        
        # Department relationship
        dept_id = f"DEPT_{po.department}"
        self.graph.add_edge(po.id, dept_id, relation='REQUESTED_BY')
        
        # Approver relationships
        for approval in po.approvals:
            approver_id = f"APPROVER_{approval.approver}"
            self.graph.add_edge(
                po.id, 
                approver_id, 
                relation='REQUIRES_APPROVAL',
                status=approval.status,
                timestamp=approval.timestamp
            )
        
        # Line items (as properties for now)
        for item in po.line_items:
            item_id = f"ITEM_{item.id}"
            self.graph.add_node(
                item_id,
                type='LineItem',
                description=item.description,
                item_code=item.item_code,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total=item.total
            )
            self.graph.add_edge(po.id, item_id, relation='CONTAINS')
            self.graph.add_edge(item_id, po.vendor_id, relation='SUPPLIED_BY')
    
    def add_goods_receipt(self, gr: GoodsReceipt, workflow: P2PWorkflow):
        """Add goods receipt and relationships"""
        self.graph.add_node(
            gr.id,
            type='GoodsReceipt',
            amount=gr.total_amount,
            status=gr.status.value,
            receipt_date=gr.receipt_date,
            quality_checked=gr.quality_checked,
            blocked=gr.status == GRStatus.BLOCKED,
            blocked_reason=gr.blocked_reason
        )
        
        # Link to PO
        if gr.po_id in workflow.purchase_orders:
            self.graph.add_edge(gr.id, gr.po_id, relation='VALIDATES')
    
    def add_invoice(self, invoice: Invoice, workflow: P2PWorkflow):
        """Add invoice and relationships"""
        self.graph.add_node(
            invoice.id,
            type='Invoice',
            amount=invoice.total_amount,
            status=invoice.status.value,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
            blocked=invoice.status == InvoiceStatus.BLOCKED,
            blocked_reason=invoice.blocked_reason
        )
        
        # Link to PO and GR
        if invoice.po_id in workflow.purchase_orders:
            self.graph.add_edge(invoice.id, invoice.po_id, relation='REFERENCES_PO')
        if invoice.gr_id in workflow.goods_receipts:
            self.graph.add_edge(invoice.id, invoice.gr_id, relation='REFERENCES_GR')
        
        # Link to vendor
        self.graph.add_edge(invoice.id, invoice.vendor_id, relation='FROM_VENDOR')
        
        # Approver relationships
        for approval in invoice.approvals:
            approver_id = f"APPROVER_{approval.approver}"
            self.graph.add_edge(
                invoice.id,
                approver_id,
                relation='REQUIRES_APPROVAL',
                status=approval.status,
                timestamp=approval.timestamp
            )
    
    def _add_product_categories(self, workflow: P2PWorkflow):
        """Infer and add product categories from line items"""
        category_keywords = {
            'IT Equipment': ['laptop', 'computer', 'monitor', 'keyboard', 'mouse', 'software'],
            'Office Supplies': ['paper', 'pen', 'pencil', 'sticky', 'folder', 'binder'],
            'Manufacturing': ['printer', 'cnc', 'industrial', 'equipment', 'machine'],
            'Services': ['consulting', 'training', 'service', 'support', 'maintenance']
        }
        
        for po in workflow.purchase_orders.values():
            for item in po.line_items:
                item_id = f"ITEM_{item.id}"
                desc_lower = item.description.lower()
                
                category = 'Other'
                for cat, keywords in category_keywords.items():
                    if any(keyword in desc_lower for keyword in keywords):
                        category = cat
                        break
                
                if self.graph.has_node(item_id):
                    self.graph.nodes[item_id]['category'] = category
                    
                    # Add category node
                    cat_id = f"CAT_{category}"
                    if not self.graph.has_node(cat_id):
                        self.graph.add_node(cat_id, type='Category', name=category)
                    
                    self.graph.add_edge(item_id, cat_id, relation='BELONGS_TO_CATEGORY')
    
    # REASONING METHODS
    
    def detect_fraud_patterns(self) -> List[Dict]:
        """Detect suspicious patterns indicating potential fraud"""
        print("\n=== Fraud Detection Analysis ===")
        suspicious_items = []
        
        # 1. Vendors with unusual invoice amounts
        vendors = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Vendor']
        
        for vendor_id in vendors:
            invoices = self._get_vendor_invoices(vendor_id)
            if len(invoices) >= 2:
                amounts = [self.graph.nodes[inv]['amount'] for inv in invoices]
                avg_amount = statistics.mean(amounts)
                
                for invoice_id in invoices:
                    invoice_amount = self.graph.nodes[invoice_id]['amount']
                    if invoice_amount > avg_amount * 3:
                        suspicious_items.append({
                            'type': 'Unusual Invoice Amount',
                            'severity': 'HIGH',
                            'vendor': self.graph.nodes[vendor_id]['name'],
                            'invoice_id': invoice_id,
                            'amount': invoice_amount,
                            'average': avg_amount,
                            'reason': f'Invoice amount is {invoice_amount/avg_amount:.1f}x the average'
                        })
        
        # 2. Split invoicing detection (multiple small invoices to avoid approval thresholds)
        for vendor_id in vendors:
            recent_invoices = self._get_recent_invoices(vendor_id, days=30)
            if len(recent_invoices) >= 3:
                total = sum(self.graph.nodes[inv]['amount'] for inv in recent_invoices)
                if total > 10000:  # Threshold for high-value purchases
                    suspicious_items.append({
                        'type': 'Possible Split Invoicing',
                        'severity': 'MEDIUM',
                        'vendor': self.graph.nodes[vendor_id]['name'],
                        'invoice_count': len(recent_invoices),
                        'total_amount': total,
                        'reason': f'{len(recent_invoices)} invoices totaling ${total:,.2f} in 30 days'
                    })
        
        # 3. Blocked document patterns
        for vendor_id in vendors:
            blocked_docs = self._get_blocked_documents(vendor_id)
            if len(blocked_docs) >= 2:
                suspicious_items.append({
                    'type': 'Multiple Blocked Documents',
                    'severity': 'HIGH',
                    'vendor': self.graph.nodes[vendor_id]['name'],
                    'blocked_count': len(blocked_docs),
                    'documents': blocked_docs,
                    'reason': f'Vendor has {len(blocked_docs)} blocked documents'
                })
        
        return suspicious_items
    
    def calculate_vendor_risk_scores(self) -> Dict[str, Dict]:
        """Calculate risk scores for all vendors based on graph patterns"""
        print("\n=== Vendor Risk Assessment ===")
        risk_scores = {}
        
        vendors = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Vendor']
        
        for vendor_id in vendors:
            score = 0
            factors = []
            
            # Factor 1: Blocked documents
            blocked_docs = self._get_blocked_documents(vendor_id)
            if blocked_docs:
                blocked_score = len(blocked_docs) * 20
                score += blocked_score
                factors.append(f"Blocked documents: +{blocked_score}")
            
            # Factor 2: Quality rejections
            rejected_grs = self._get_rejected_goods_receipts(vendor_id)
            if rejected_grs:
                quality_score = len(rejected_grs) * 30
                score += quality_score
                factors.append(f"Quality rejections: +{quality_score}")
            
            # Factor 3: Overdue invoices
            overdue = self._get_overdue_invoices(vendor_id)
            if overdue:
                overdue_score = len(overdue) * 15
                score += overdue_score
                factors.append(f"Overdue invoices: +{overdue_score}")
            
            # Factor 4: Transaction volume (high volume = lower risk if no issues)
            transaction_count = len(self._get_vendor_pos(vendor_id))
            if transaction_count > 5 and score == 0:
                score -= 10
                factors.append(f"High transaction volume: -10")
            
            risk_level = 'LOW' if score < 30 else 'MEDIUM' if score < 60 else 'HIGH'
            
            risk_scores[vendor_id] = {
                'vendor_name': self.graph.nodes[vendor_id]['name'],
                'risk_score': max(0, score),
                'risk_level': risk_level,
                'factors': factors,
                'transaction_count': transaction_count
            }
        
        return risk_scores
    
    def recommend_vendors(self, category: str, exclude_high_risk: bool = True) -> List[Dict]:
        """Recommend vendors for a product category based on performance"""
        print(f"\n=== Vendor Recommendations for {category} ===")
        recommendations = []
        
        # Find vendors supplying this category
        cat_id = f"CAT_{category}"
        if not self.graph.has_node(cat_id):
            return recommendations
        
        # Get all items in this category
        items = [n for n, d in self.graph.nodes(data=True) 
                if d.get('type') == 'LineItem' and d.get('category') == category]
        
        # Get vendors for these items
        vendor_performance = defaultdict(lambda: {'prices': [], 'quality_issues': 0, 'blocked': 0})
        
        for item_id in items:
            # Get vendor
            vendors = [v for u, v, d in self.graph.out_edges(item_id, data=True) 
                      if d.get('relation') == 'SUPPLIED_BY']
            
            if vendors:
                vendor_id = vendors[0]
                price = self.graph.nodes[item_id].get('unit_price', 0)
                vendor_performance[vendor_id]['prices'].append(price)
                
                # Check for quality issues
                po_id = [u for u, v, d in self.graph.in_edges(item_id, data=True) 
                        if d.get('relation') == 'CONTAINS'][0]
                grs = [v for u, v, d in self.graph.out_edges(po_id, data=True) 
                      if self.graph.nodes[v].get('type') == 'GoodsReceipt']
                
                for gr_id in grs:
                    if self.graph.nodes[gr_id]['status'] == 'Rejected':
                        vendor_performance[vendor_id]['quality_issues'] += 1
                    if self.graph.nodes[gr_id].get('blocked', False):
                        vendor_performance[vendor_id]['blocked'] += 1
        
        # Calculate risk scores
        risk_scores = self.calculate_vendor_risk_scores()
        
        # Build recommendations
        for vendor_id, perf in vendor_performance.items():
            if not perf['prices']:
                continue
            
            vendor_name = self.graph.nodes[vendor_id]['name']
            avg_price = statistics.mean(perf['prices'])
            risk_info = risk_scores.get(vendor_id, {})
            risk_score = risk_info.get('risk_score', 0)
            
            # Skip high-risk vendors if requested
            if exclude_high_risk and risk_score >= 60:
                continue
            
            recommendations.append({
                'vendor_id': vendor_id,
                'vendor_name': vendor_name,
                'avg_price': avg_price,
                'risk_score': risk_score,
                'risk_level': risk_info.get('risk_level', 'UNKNOWN'),
                'quality_issues': perf['quality_issues'],
                'blocked_count': perf['blocked'],
                'transaction_count': len(self._get_vendor_pos(vendor_id))
            })
        
        # Sort by risk score (ascending) and price (ascending)
        recommendations.sort(key=lambda x: (x['risk_score'], x['avg_price']))
        
        return recommendations
    
    def detect_three_way_match_issues(self) -> List[Dict]:
        """Detect issues in three-way matching (PO -> GR -> Invoice)"""
        print("\n=== Three-Way Match Validation ===")
        issues = []
        
        invoices = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Invoice']
        
        for invoice_id in invoices:
            # Get related PO and GR
            po_edges = [v for u, v, d in self.graph.out_edges(invoice_id, data=True) 
                       if d.get('relation') == 'REFERENCES_PO']
            gr_edges = [v for u, v, d in self.graph.out_edges(invoice_id, data=True) 
                       if d.get('relation') == 'REFERENCES_GR']
            
            if not po_edges or not gr_edges:
                issues.append({
                    'invoice_id': invoice_id,
                    'issue': 'Missing PO or GR reference',
                    'severity': 'HIGH'
                })
                continue
            
            po_id = po_edges[0]
            gr_id = gr_edges[0]
            
            # Check amounts
            invoice_amount = self.graph.nodes[invoice_id]['amount']
            po_amount = self.graph.nodes[po_id]['amount']
            gr_amount = self.graph.nodes[gr_id]['amount']
            
            # Allow 5% variance
            if abs(invoice_amount - po_amount) / po_amount > 0.05:
                issues.append({
                    'invoice_id': invoice_id,
                    'po_id': po_id,
                    'issue': f'Invoice amount ${invoice_amount:,.2f} differs from PO ${po_amount:,.2f}',
                    'severity': 'MEDIUM',
                    'variance_pct': abs(invoice_amount - po_amount) / po_amount * 100
                })
            
            # Check if GR was accepted
            if self.graph.nodes[gr_id]['status'] != 'Accepted':
                issues.append({
                    'invoice_id': invoice_id,
                    'gr_id': gr_id,
                    'issue': f'GR not accepted (status: {self.graph.nodes[gr_id]["status"]})',
                    'severity': 'HIGH'
                })
        
        return issues
    
    def predict_approval_delays(self) -> List[Dict]:
        """Predict which documents might face approval delays"""
        print("\n=== Approval Delay Prediction ===")
        predictions = []
        
        # Analyze pending approvals
        pending_pos = [n for n, d in self.graph.nodes(data=True) 
                      if d.get('type') == 'PurchaseOrder' and d.get('status') == 'Pending Approval']
        pending_invs = [n for n, d in self.graph.nodes(data=True) 
                       if d.get('type') == 'Invoice' and d.get('status') == 'Pending Approval']
        
        for doc_id in pending_pos + pending_invs:
            doc_type = self.graph.nodes[doc_id]['type']
            amount = self.graph.nodes[doc_id]['amount']
            
            # Get approvers
            approvers = [v for u, v, d in self.graph.out_edges(doc_id, data=True) 
                        if d.get('relation') == 'REQUIRES_APPROVAL' and d.get('status') == 'Pending']
            
            delay_factors = []
            risk_score = 0
            
            # Factor 1: High amount
            if amount > 10000:
                risk_score += 30
                delay_factors.append('High amount requiring executive approval')
            
            # Factor 2: Multiple approvers
            if len(approvers) >= 3:
                risk_score += 20
                delay_factors.append(f'{len(approvers)} approvers required')
            
            # Factor 3: Vendor risk
            vendor_edges = [v for u, v, d in self.graph.out_edges(doc_id, data=True) 
                           if d.get('relation') == 'FROM_VENDOR']
            if vendor_edges:
                vendor_id = vendor_edges[0]
                blocked_docs = self._get_blocked_documents(vendor_id)
                if blocked_docs:
                    risk_score += 25
                    delay_factors.append(f'Vendor has {len(blocked_docs)} blocked documents')
            
            if risk_score >= 30:
                predictions.append({
                    'document_id': doc_id,
                    'document_type': doc_type,
                    'amount': amount,
                    'delay_risk_score': risk_score,
                    'risk_level': 'HIGH' if risk_score >= 60 else 'MEDIUM',
                    'factors': delay_factors,
                    'pending_approvers': len(approvers)
                })
        
        return predictions
    
    def find_consolidation_opportunities(self) -> List[Dict]:
        """Find opportunities to consolidate vendors"""
        print("\n=== Vendor Consolidation Opportunities ===")
        opportunities = []
        
        # Group vendors by category
        categories = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Category']
        
        for cat_id in categories:
            category_name = self.graph.nodes[cat_id]['name']
            
            # Get items in this category
            items = [u for u, v, d in self.graph.in_edges(cat_id, data=True) 
                    if d.get('relation') == 'BELONGS_TO_CATEGORY']
            
            # Get vendors for these items
            vendors_in_category = set()
            for item_id in items:
                vendors = [v for u, v, d in self.graph.out_edges(item_id, data=True) 
                          if d.get('relation') == 'SUPPLIED_BY']
                vendors_in_category.update(vendors)
            
            if len(vendors_in_category) >= 3:
                # Calculate spend per vendor
                vendor_spend = {}
                for vendor_id in vendors_in_category:
                    pos = self._get_vendor_pos(vendor_id)
                    total = sum(self.graph.nodes[po]['amount'] for po in pos)
                    vendor_spend[vendor_id] = {
                        'name': self.graph.nodes[vendor_id]['name'],
                        'spend': total,
                        'transaction_count': len(pos)
                    }
                
                opportunities.append({
                    'category': category_name,
                    'vendor_count': len(vendors_in_category),
                    'total_spend': sum(v['spend'] for v in vendor_spend.values()),
                    'vendors': vendor_spend,
                    'recommendation': f'Consider consolidating {len(vendors_in_category)} vendors for {category_name}'
                })
        
        return opportunities
    
    # HELPER METHODS
    
    def _get_vendor_pos(self, vendor_id: str) -> List[str]:
        """Get all POs for a vendor"""
        return [u for u, v, d in self.graph.in_edges(vendor_id, data=True) 
                if d.get('relation') == 'FROM_VENDOR' and 
                self.graph.nodes[u].get('type') == 'PurchaseOrder']
    
    def _get_vendor_invoices(self, vendor_id: str) -> List[str]:
        """Get all invoices for a vendor"""
        return [u for u, v, d in self.graph.in_edges(vendor_id, data=True) 
                if d.get('relation') == 'FROM_VENDOR' and 
                self.graph.nodes[u].get('type') == 'Invoice']
    
    def _get_recent_invoices(self, vendor_id: str, days: int = 30) -> List[str]:
        """Get recent invoices for a vendor"""
        cutoff = datetime.now() - timedelta(days=days)
        invoices = self._get_vendor_invoices(vendor_id)
        return [inv for inv in invoices 
                if self.graph.nodes[inv].get('invoice_date', datetime.min) > cutoff]
    
    def _get_blocked_documents(self, vendor_id: str) -> List[str]:
        """Get blocked documents for a vendor"""
        all_docs = []
        all_docs.extend(self._get_vendor_pos(vendor_id))
        all_docs.extend(self._get_vendor_invoices(vendor_id))
        return [doc for doc in all_docs if self.graph.nodes[doc].get('blocked', False)]
    
    def _get_rejected_goods_receipts(self, vendor_id: str) -> List[str]:
        """Get rejected goods receipts for a vendor"""
        pos = self._get_vendor_pos(vendor_id)
        rejected = []
        for po_id in pos:
            grs = [v for u, v, d in self.graph.out_edges(po_id, data=True) 
                  if self.graph.nodes[v].get('type') == 'GoodsReceipt']
            rejected.extend([gr for gr in grs if self.graph.nodes[gr]['status'] == 'Rejected'])
        return rejected
    
    def _get_overdue_invoices(self, vendor_id: str) -> List[str]:
        """Get overdue invoices for a vendor"""
        invoices = self._get_vendor_invoices(vendor_id)
        return [inv for inv in invoices 
                if self.graph.nodes[inv]['status'] == 'Overdue']
    
    def generate_comprehensive_report(self, workflow: P2PWorkflow) -> Dict:
        """Generate a comprehensive KG reasoning report"""
        print("\n" + "="*60)
        print("KNOWLEDGE GRAPH REASONING REPORT")
        print("="*60)
        
        report = {
            'fraud_patterns': self.detect_fraud_patterns(),
            'vendor_risks': self.calculate_vendor_risk_scores(),
            'three_way_match_issues': self.detect_three_way_match_issues(),
            'approval_delays': self.predict_approval_delays(),
            'consolidation_opportunities': self.find_consolidation_opportunities(),
            'graph_stats': {
                'total_nodes': self.graph.number_of_nodes(),
                'total_edges': self.graph.number_of_edges(),
                'total_vendors': len([n for n, d in self.graph.nodes(data=True) 
                                     if d.get('type') == 'Vendor']),
                'total_pos': len([n for n, d in self.graph.nodes(data=True) 
                                 if d.get('type') == 'PurchaseOrder']),
                'total_invoices': len([n for n, d in self.graph.nodes(data=True) 
                                      if d.get('type') == 'Invoice'])
            }
        }
        
        return report
