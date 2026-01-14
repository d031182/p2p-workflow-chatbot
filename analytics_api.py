"""
Analytics API for risk and outlier analysis
Provides data for visualization dashboard
"""
import numpy as np
from typing import Dict, List
from datetime import datetime


def calculate_risk_analysis(workflow) -> Dict:
    """Calculate risk distribution across all documents"""
    all_docs = []
    
    # Collect all documents
    for po in workflow.purchase_orders.values():
        all_docs.append({
            'id': po.id,
            'number': po.po_number,
            'type': 'PO',
            'amount': po.total_amount,
            'status': po.status.value,
            'doc': po
        })
    
    for inv in workflow.invoices.values():
        all_docs.append({
            'id': inv.id,
            'number': inv.invoice_number,
            'type': 'Invoice',
            'amount': inv.total_amount,
            'status': inv.status.value,
            'doc': inv
        })
    
    # Calculate risk for each document
    risk_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    risk_amounts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    high_risk_docs = []
    
    for doc_data in all_docs:
        doc = doc_data['doc']
        risk_score = 0
        risk_factors = []
        
        # Amount risk
        if doc.total_amount > 50000:
            risk_score += 3
            risk_factors.append("High value")
        elif doc.total_amount > 10000:
            risk_score += 1
            risk_factors.append("Medium value")
        
        # Status risk
        if doc_data['status'] == "Blocked":
            risk_score += 5
            risk_factors.append("Blocked")
        elif doc_data['status'] == "Pending Approval":
            risk_score += 2
            risk_factors.append("Pending approval")
        
        # Overdue risk (invoices)
        if doc_data['type'] == 'Invoice' and hasattr(doc, 'due_date'):
            days_until_due = (doc.due_date - datetime.now()).days
            if days_until_due < 0:
                risk_score += 4
                risk_factors.append(f"Overdue")
        
        # Determine risk level
        if risk_score >= 7:
            risk_level = 'critical'
        elif risk_score >= 4:
            risk_level = 'high'
        elif risk_score >= 2:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        risk_counts[risk_level] += 1
        risk_amounts[risk_level] += doc.total_amount
        
        if risk_level in ['high', 'critical']:
            high_risk_docs.append({
                'number': doc_data['number'],
                'type': doc_data['type'],
                'amount': doc.total_amount,
                'risk': risk_level.upper(),
                'score': risk_score,
                'factors': risk_factors
            })
    
    return {
        'counts': risk_counts,
        'amounts': risk_amounts,
        'highRiskDocs': high_risk_docs
    }


def calculate_outlier_analysis(workflow) -> Dict:
    """Calculate outlier statistics and visualization data"""
    
    # Get PO data
    pos = list(workflow.purchase_orders.values())
    po_amounts = [po.total_amount for po in pos]
    po_mean = np.mean(po_amounts)
    po_std = np.std(po_amounts)
    
    # Get Invoice data
    invs = list(workflow.invoices.values())
    inv_amounts = [inv.total_amount for inv in invs]
    inv_mean = np.mean(inv_amounts)
    inv_std = np.std(inv_amounts)
    
    # Find PO outliers
    po_normal = []
    po_outliers = []
    po_outlier_docs = []
    
    for i, po in enumerate(pos):
        z_score = abs(po.total_amount - po_mean) / po_std if po_std > 0 else 0
        point = {'x': i, 'y': po.total_amount}
        
        if z_score > 2.0:
            po_outliers.append(point)
            po_outlier_docs.append({
                'number': po.po_number,
                'type': 'PO',
                'amount': po.total_amount,
                'z_score': round(z_score, 2),
                'deviation': round(po.total_amount - po_mean, 2),
                'vendor': po.vendor_name
            })
        else:
            po_normal.append(point)
    
    # Find Invoice outliers
    inv_normal = []
    inv_outliers = []
    inv_outlier_docs = []
    
    for i, inv in enumerate(invs):
        z_score = abs(inv.total_amount - inv_mean) / inv_std if inv_std > 0 else 0
        point = {'x': i, 'y': inv.total_amount}
        
        if z_score > 2.0:
            inv_outliers.append(point)
            inv_outlier_docs.append({
                'number': inv.invoice_number,
                'type': 'Invoice',
                'amount': inv.total_amount,
                'z_score': round(z_score, 2),
                'deviation': round(inv.total_amount - inv_mean, 2),
                'vendor': inv.vendor_name
            })
        else:
            inv_normal.append(point)
    
    # Combine all outliers
    all_outliers = po_outlier_docs + inv_outlier_docs
    all_outliers.sort(key=lambda x: x['z_score'], reverse=True)
    
    return {
        'po': {
            'normal': po_normal,
            'outliers': po_outliers
        },
        'invoice': {
            'normal': inv_normal,
            'outliers': inv_outliers
        },
        'po_stats': {
            'mean': round(po_mean, 2),
            'median': round(np.median(po_amounts), 2),
            'std_dev': round(po_std, 2),
            'outlier_count': len(po_outliers)
        },
        'inv_stats': {
            'mean': round(inv_mean, 2),
            'median': round(np.median(inv_amounts), 2),
            'std_dev': round(inv_std, 2),
            'outlier_count': len(inv_outliers)
        },
        'all': all_outliers[:20]  # Top 20 outliers
    }


def get_analytics_data(workflow) -> Dict:
    """Get complete analytics data for dashboard"""
    return {
        'risk': calculate_risk_analysis(workflow),
        'outliers': calculate_outlier_analysis(workflow)
    }
