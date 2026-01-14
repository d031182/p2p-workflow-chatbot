"""
Tool-Enhanced Chatbot with Function Calling
The chatbot can use tools/functions to perform tasks like:
- Analyze outliers
- Generate reports
- Query databases
- Call external APIs
"""
from typing import Dict, List, Optional, Callable
import json
import numpy as np
from datetime import datetime
from chatbot import P2PChatbot


class P2PChatbotWithTools(P2PChatbot):
    """
    Chatbot enhanced with tool/function calling capabilities
    Can use external functions to perform analysis and tasks
    """
    
    def __init__(self, workflow, llm_backend: str = "none"):
        super().__init__(workflow)
        self.llm_backend = llm_backend
        self.llm = None
        
        # Register available tools
        self.tools = self._register_tools()
        
        # All tools enabled by default (can be configured via enabled_tools)
        self.enabled_tools = list(self.tools.keys())
        
        if llm_backend == "openai":
            self._init_openai()
        else:
            print("✓ Tool-enhanced chatbot initialized")
            print(f"  Available tools: {len(self.tools)}")
            print("  Tools: " + ", ".join(self.tools.keys()))
    
    def _register_tools(self) -> Dict[str, Dict]:
        """
        Register available tools/functions
        Each tool has: name, description, function, parameters
        """
        return {
            "analyze_outliers": {
                "name": "analyze_outliers",
                "description": "Identify outliers in purchase orders, invoices, or goods receipts. Returns documents with unusual amounts.",
                "function": self._tool_analyze_outliers,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "enum": ["purchase_orders", "invoices", "goods_receipts"],
                            "description": "Type of document to analyze"
                        },
                        "threshold": {
                            "type": "number",
                            "description": "Standard deviations from mean (default: 2.0)"
                        }
                    },
                    "required": ["document_type"]
                }
            },
            
            "calculate_statistics": {
                "name": "calculate_statistics",
                "description": "Calculate detailed statistics (mean, median, std dev, percentiles) for document amounts",
                "function": self._tool_calculate_statistics,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "enum": ["purchase_orders", "invoices", "goods_receipts"],
                            "description": "Type of document to analyze"
                        }
                    },
                    "required": ["document_type"]
                }
            },
            
            "find_spending_trends": {
                "name": "find_spending_trends",
                "description": "Analyze spending trends by department, vendor, or time period",
                "function": self._tool_find_spending_trends,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_by": {
                            "type": "string",
                            "enum": ["department", "vendor", "month"],
                            "description": "How to group the analysis"
                        }
                    },
                    "required": ["group_by"]
                }
            },
            
            "predict_payment_date": {
                "name": "predict_payment_date",
                "description": "Predict when an invoice will be paid based on historical patterns",
                "function": self._tool_predict_payment_date,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "invoice_id": {
                            "type": "string",
                            "description": "Invoice ID to predict payment for"
                        }
                    },
                    "required": ["invoice_id"]
                }
            },
            
            "risk_assessment": {
                "name": "risk_assessment",
                "description": "Assess risk level of pending documents based on amount, complexity, history",
                "function": self._tool_risk_assessment,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID to assess"
                        }
                    },
                    "required": ["document_id"]
                }
            },
            
            "explain_blocked_document": {
                "name": "explain_blocked_document",
                "description": "Use Knowledge Graph reasoning to explain why a document is blocked and provide actionable insights",
                "function": self._tool_explain_blocked_document,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID to explain (PO, GR, or Invoice ID)"
                        }
                    },
                    "required": ["document_id"]
                }
            }
        }
    
    # ==================== TOOL IMPLEMENTATIONS ====================
    
    def _tool_analyze_outliers(self, document_type: str, threshold: float = 2.0) -> Dict:
        """
        Identify outliers using statistical analysis
        Uses Z-score method: |value - mean| / std_dev > threshold
        """
        if document_type == "purchase_orders":
            documents = list(self.workflow.purchase_orders.values())
        elif document_type == "invoices":
            documents = list(self.workflow.invoices.values())
        elif document_type == "goods_receipts":
            documents = list(self.workflow.goods_receipts.values())
        else:
            return {"error": "Invalid document type"}
        
        # Get amounts
        amounts = [doc.total_amount for doc in documents]
        
        if len(amounts) < 3:
            return {"error": "Not enough data for outlier analysis"}
        
        # Calculate statistics
        mean = np.mean(amounts)
        std_dev = np.std(amounts)
        
        # Find outliers
        outliers = []
        for doc in documents:
            z_score = abs(doc.total_amount - mean) / std_dev if std_dev > 0 else 0
            
            if z_score > threshold:
                outlier_info = {
                    "id": doc.id,
                    "number": getattr(doc, 'po_number', None) or getattr(doc, 'invoice_number', None) or getattr(doc, 'gr_number', None),
                    "amount": doc.total_amount,
                    "z_score": round(z_score, 2),
                    "deviation_from_mean": round(doc.total_amount - mean, 2),
                    "vendor": getattr(doc, 'vendor_name', 'N/A')
                }
                outliers.append(outlier_info)
        
        # Sort by z-score descending
        outliers.sort(key=lambda x: x['z_score'], reverse=True)
        
        return {
            "document_type": document_type,
            "total_documents": len(documents),
            "mean_amount": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "threshold": threshold,
            "outliers_found": len(outliers),
            "outliers": outliers[:10]  # Top 10 outliers
        }
    
    def _tool_calculate_statistics(self, document_type: str) -> Dict:
        """Calculate comprehensive statistics"""
        if document_type == "purchase_orders":
            documents = list(self.workflow.purchase_orders.values())
        elif document_type == "invoices":
            documents = list(self.workflow.invoices.values())
        elif document_type == "goods_receipts":
            documents = list(self.workflow.goods_receipts.values())
        else:
            return {"error": "Invalid document type"}
        
        amounts = [doc.total_amount for doc in documents]
        
        if not amounts:
            return {"error": "No documents found"}
        
        return {
            "document_type": document_type,
            "count": len(amounts),
            "mean": round(np.mean(amounts), 2),
            "median": round(np.median(amounts), 2),
            "std_dev": round(np.std(amounts), 2),
            "min": round(min(amounts), 2),
            "max": round(max(amounts), 2),
            "percentile_25": round(np.percentile(amounts, 25), 2),
            "percentile_50": round(np.percentile(amounts, 50), 2),
            "percentile_75": round(np.percentile(amounts, 75), 2),
            "percentile_95": round(np.percentile(amounts, 95), 2),
            "total": round(sum(amounts), 2)
        }
    
    def _tool_find_spending_trends(self, group_by: str) -> Dict:
        """Analyze spending trends"""
        pos = list(self.workflow.purchase_orders.values())
        
        if group_by == "department":
            trends = {}
            for po in pos:
                dept = po.department
                if dept not in trends:
                    trends[dept] = {"count": 0, "total": 0}
                trends[dept]["count"] += 1
                trends[dept]["total"] += po.total_amount
        
        elif group_by == "vendor":
            trends = {}
            for po in pos:
                vendor = po.vendor_name
                if vendor not in trends:
                    trends[vendor] = {"count": 0, "total": 0}
                trends[vendor]["count"] += 1
                trends[vendor]["total"] += po.total_amount
        
        elif group_by == "month":
            trends = {}
            for po in pos:
                month = po.creation_date.strftime("%Y-%m")
                if month not in trends:
                    trends[month] = {"count": 0, "total": 0}
                trends[month]["count"] += 1
                trends[month]["total"] += po.total_amount
        
        else:
            return {"error": "Invalid group_by parameter"}
        
        # Sort by total descending
        sorted_trends = sorted(
            [{"category": k, **v} for k, v in trends.items()],
            key=lambda x: x["total"],
            reverse=True
        )
        
        return {
            "group_by": group_by,
            "categories": len(sorted_trends),
            "trends": sorted_trends[:10]  # Top 10
        }
    
    def _tool_predict_payment_date(self, invoice_id: str) -> Dict:
        """Predict payment date based on patterns"""
        invoice = self.workflow.invoices.get(invoice_id)
        
        if not invoice:
            return {"error": "Invoice not found"}
        
        # Simple prediction based on payment terms
        if invoice.status.value == "Paid":
            return {
                "invoice_id": invoice_id,
                "status": "Already paid",
                "payment_date": invoice.payment_date.strftime("%Y-%m-%d") if invoice.payment_date else "N/A"
            }
        
        # Predict based on due date and historical data
        days_until_due = (invoice.due_date - datetime.now()).days
        
        if days_until_due < 0:
            prediction = "Overdue - immediate attention needed"
            confidence = "HIGH"
        elif days_until_due < 7:
            prediction = f"Within {days_until_due} days (by due date)"
            confidence = "HIGH"
        else:
            prediction = f"Approximately {days_until_due} days (by due date)"
            confidence = "MEDIUM"
        
        return {
            "invoice_id": invoice_id,
            "invoice_number": invoice.invoice_number,
            "current_status": invoice.status.value,
            "due_date": invoice.due_date.strftime("%Y-%m-%d"),
            "days_until_due": days_until_due,
            "prediction": prediction,
            "confidence": confidence
        }
    
    def _tool_risk_assessment(self, document_id: str) -> Dict:
        """Assess risk level of a document"""
        # Try to find document in all collections
        doc = None
        doc_type = None
        
        if document_id in self.workflow.purchase_orders:
            doc = self.workflow.purchase_orders[document_id]
            doc_type = "Purchase Order"
        elif document_id in self.workflow.invoices:
            doc = self.workflow.invoices[document_id]
            doc_type = "Invoice"
        elif document_id in self.workflow.goods_receipts:
            doc = self.workflow.goods_receipts[document_id]
            doc_type = "Goods Receipt"
        
        if not doc:
            return {"error": "Document not found"}
        
        # Calculate risk score
        risk_score = 0
        risk_factors = []
        
        # Amount risk
        if doc.total_amount > 50000:
            risk_score += 3
            risk_factors.append("High value transaction")
        elif doc.total_amount > 10000:
            risk_score += 1
            risk_factors.append("Medium value transaction")
        
        # Status risk
        if hasattr(doc, 'status'):
            if doc.status.value == "Blocked":
                risk_score += 5
                risk_factors.append("Document is blocked")
            elif doc.status.value == "Pending Approval":
                risk_score += 2
                risk_factors.append("Awaiting approval")
        
        # Overdue risk (for invoices)
        if doc_type == "Invoice" and hasattr(doc, 'due_date'):
            days_until_due = (doc.due_date - datetime.now()).days
            if days_until_due < 0:
                risk_score += 4
                risk_factors.append(f"Overdue by {abs(days_until_due)} days")
        
        # Determine risk level
        if risk_score >= 7:
            risk_level = "CRITICAL"
        elif risk_score >= 4:
            risk_level = "HIGH"
        elif risk_score >= 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "document_id": document_id,
            "document_type": doc_type,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendation": self._get_risk_recommendation(risk_level)
        }
    
    def _tool_explain_blocked_document(self, document_id: str) -> Dict:
        """Use Knowledge Graph reasoning to explain why a document is blocked"""
        try:
            from kg_reasoning import P2PKnowledgeGraph
            
            # Find the document
            doc = None
            doc_type = None
            
            if document_id in self.workflow.purchase_orders:
                doc = self.workflow.purchase_orders[document_id]
                doc_type = "Purchase Order"
            elif document_id in self.workflow.invoices:
                doc = self.workflow.invoices[document_id]
                doc_type = "Invoice"
            elif document_id in self.workflow.goods_receipts:
                doc = self.workflow.goods_receipts[document_id]
                doc_type = "Goods Receipt"
            
            if not doc:
                return {"error": "Document not found"}
            
            # Check if document is actually blocked
            is_blocked = doc.status.value == "Blocked" if hasattr(doc, 'status') else False
            
            if not is_blocked:
                return {
                    "document_id": document_id,
                    "doc_type": doc_type,
                    "is_blocked": False,
                    "status": doc.status.value,
                    "message": f"This {doc_type} is not blocked. Current status: {doc.status.value}"
                }
            
            # Build KG for analysis
            kg = P2PKnowledgeGraph()
            kg.build_graph_from_workflow(self.workflow)
            
            # Get comprehensive insights
            vendor_risks = kg.calculate_vendor_risk_scores()
            fraud_patterns = kg.detect_fraud_patterns()
            match_issues = kg.detect_three_way_match_issues()
            
            # Analyze why this document is blocked
            reasons = []
            recommendations = []
            
            # Direct blocking reason
            if hasattr(doc, 'blocked_reason') and doc.blocked_reason:
                reasons.append({
                    "category": "Direct Reason",
                    "description": doc.blocked_reason,
                    "severity": "HIGH"
                })
            
            # Check vendor risk
            vendor_id = getattr(doc, 'vendor_id', None)
            if vendor_id and vendor_id in vendor_risks:
                risk_info = vendor_risks[vendor_id]
                if risk_info['risk_level'] in ['HIGH', 'MEDIUM']:
                    reasons.append({
                        "category": "Vendor Risk",
                        "description": f"Vendor {risk_info['vendor_name']} has {risk_info['risk_level']} risk (score: {risk_info['risk_score']})",
                        "severity": risk_info['risk_level'],
                        "factors": risk_info['factors']
                    })
                    recommendations.append(f"Review vendor {risk_info['vendor_name']}'s transaction history before unblocking")
            
            # Check for fraud patterns
            for pattern in fraud_patterns:
                if pattern.get('vendor') == getattr(doc, 'vendor_name', None):
                    reasons.append({
                        "category": "Fraud Detection",
                        "description": f"{pattern['type']}: {pattern['reason']}",
                        "severity": pattern['severity']
                    })
                    recommendations.append("Conduct thorough fraud investigation before proceeding")
            
            # Check three-way match issues (for invoices)
            if doc_type == "Invoice":
                for issue in match_issues:
                    if issue.get('invoice_id') == document_id:
                        reasons.append({
                            "category": "Three-Way Match Issue",
                            "description": issue['issue'],
                            "severity": issue['severity']
                        })
                        recommendations.append("Verify PO-GR-Invoice matching before unblocking")
            
            # Amount-based analysis
            if doc.total_amount > 50000:
                reasons.append({
                    "category": "High Value Transaction",
                    "description": f"Amount ${doc.total_amount:,.2f} exceeds standard threshold",
                    "severity": "MEDIUM"
                })
                recommendations.append("Obtain executive approval for high-value transaction")
            
            # If no specific reasons found, provide generic analysis
            if not reasons:
                reasons.append({
                    "category": "Manual Block",
                    "description": "Document was manually blocked. No automated detection triggered.",
                    "severity": "MEDIUM"
                })
                recommendations.append("Contact the user who blocked this document for details")
            
            # Add general recommendations
            recommendations.append(f"Review all related documents in the workflow")
            if vendor_id:
                recommendations.append(f"Check other documents from this vendor")
            
            return {
                "document_id": document_id,
                "doc_type": doc_type,
                "is_blocked": True,
                "status": doc.status.value,
                "amount": doc.total_amount,
                "vendor": getattr(doc, 'vendor_name', 'N/A'),
                "reasons": reasons,
                "recommendations": recommendations,
                "insight": self._generate_insight(reasons, doc_type)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze document: {str(e)}"}
    
    def _generate_insight(self, reasons: List[Dict], doc_type: str) -> str:
        """Generate human-readable insight from reasons"""
        if not reasons:
            return f"This {doc_type} appears to be manually blocked without specific automated triggers."
        
        high_severity = [r for r in reasons if r.get('severity') == 'HIGH']
        
        if high_severity:
            main_reason = high_severity[0]
            return f"Primary concern: {main_reason['description']}. This is a high-priority issue requiring immediate attention."
        
        main_reason = reasons[0]
        return f"Main issue: {main_reason['description']}. Review and resolve before unblocking."
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "CRITICAL": "Immediate action required - escalate to management",
            "HIGH": "Priority attention needed - review within 24 hours",
            "MEDIUM": "Monitor closely - review within this week",
            "LOW": "Normal processing - standard workflow"
        }
        return recommendations.get(risk_level, "Review as needed")
    
    # ==================== TOOL EXECUTION ====================
    
    def process_message(self, user_message: str) -> dict:
        """
        Process message with tool calling capability
        """
        message = user_message.lower().strip()
        
        # Check if user wants to use a tool
        if any(keyword in message for keyword in ['outlier', 'unusual', 'anomal', 'detect']):
            if 'po' in message or 'purchase order' in message:
                result = self._tool_analyze_outliers("purchase_orders")
                return {'message': self._format_outlier_result(result)}
            elif 'invoice' in message:
                result = self._tool_analyze_outliers("invoices")
                return {'message': self._format_outlier_result(result)}
        
        if any(keyword in message for keyword in ['statistic', 'stats', 'analysis']):
            if 'po' in message or 'purchase order' in message:
                result = self._tool_calculate_statistics("purchase_orders")
                return {'message': self._format_statistics_result(result)}
            elif 'invoice' in message:
                result = self._tool_calculate_statistics("invoices")
                return {'message': self._format_statistics_result(result)}
        
        if any(keyword in message for keyword in ['trend', 'spending pattern']):
            if 'department' in message:
                result = self._tool_find_spending_trends("department")
                return {'message': self._format_trends_result(result)}
            elif 'vendor' in message:
                result = self._tool_find_spending_trends("vendor")
                return {'message': self._format_trends_result(result)}
        
        if any(keyword in message for keyword in ['risk', 'assess']):
            # Try to extract document ID from message
            words = message.split()
            for word in words:
                if '-' in word:  # Likely a document ID
                    result = self._tool_risk_assessment(word.upper())
                    return {'message': self._format_risk_result(result)}
        
        # Check for blocked document explanation requests
        if any(keyword in message for keyword in ['blocked', 'why block', 'explain block', 'why is', 'what happened']):
            # Try to extract document ID from message
            words = message.split()
            for word in words:
                if '-' in word:  # Likely a document ID
                    result = self._tool_explain_blocked_document(word.upper())
                    return {'message': self._format_blocked_explanation(result)}
        
        # Fall back to regular chatbot
        return super().process_message(user_message)
    
    # ==================== RESULT FORMATTING ====================
    
    def _format_outlier_result(self, result: Dict) -> str:
        """Format outlier analysis result with visual chart"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        import uuid
        chart_id = f"chart-{uuid.uuid4().hex[:8]}"
        
        # Prepare data for chart
        doc_type = result['document_type']
        
        # Get all documents for visualization
        if doc_type == "purchase_orders":
            documents = list(self.workflow.purchase_orders.values())
        elif doc_type == "invoices":
            documents = list(self.workflow.invoices.values())
        else:
            documents = list(self.workflow.goods_receipts.values())
        
        # Separate normal and outliers for chart
        normal_points = []
        outlier_points = []
        outlier_ids = [o['id'] for o in result['outliers']]
        
        for i, doc in enumerate(documents):
            point = {'x': i, 'y': doc.total_amount}
            if doc.id in outlier_ids:
                outlier_points.append(point)
            else:
                normal_points.append(point)
        
        # Create HTML with chart
        html = f"""
<div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">
    <h5>📊 Outlier Analysis: {doc_type.replace('_', ' ').title()}</h5>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
        <div style="background: #e7f3ff; padding: 10px; border-radius: 5px;">
            <strong>Total Documents:</strong> {result['total_documents']}
        </div>
        <div style="background: #e7f3ff; padding: 10px; border-radius: 5px;">
            <strong>Outliers Found:</strong> <span style="color: #dc3545;">{result['outliers_found']}</span>
        </div>
        <div style="background: #e7f3ff; padding: 10px; border-radius: 5px;">
            <strong>Mean Amount:</strong> ${result['mean_amount']:,.2f}
        </div>
        <div style="background: #e7f3ff; padding: 10px; border-radius: 5px;">
            <strong>Std Deviation:</strong> ${result['std_dev']:,.2f}
        </div>
    </div>
    
    <canvas id="{chart_id}" style="max-height: 300px; margin: 20px 0;"></canvas>
    
    <script>
    (function() {{
        const ctx = document.getElementById('{chart_id}').getContext('2d');
        new Chart(ctx, {{
            type: 'scatter',
            data: {{
                datasets: [
                    {{
                        label: 'Normal Documents',
                        data: {json.dumps(normal_points)},
                        backgroundColor: '#28a745',
                        pointRadius: 5
                    }},
                    {{
                        label: 'Outliers',
                        data: {json.dumps(outlier_points)},
                        backgroundColor: '#dc3545',
                        pointRadius: 8
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ 
                        title: {{ display: true, text: 'Document Index' }},
                        grid: {{ display: false }}
                    }},
                    y: {{ 
                        title: {{ display: true, text: 'Amount ($)' }},
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString();
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                            }}
                        }}
                    }},
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }}
            }}
        }});
    }})();
    </script>
"""
        
        # Add outlier details table
        if result['outliers_found'] > 0:
            html += f"""
    <div style="margin-top: 20px;">
        <h6>⚠️ Detected Outliers:</h6>
        <table style="width: 100%; font-size: 0.9em; border-collapse: collapse;">
            <thead style="background: #f8f9fa;">
                <tr>
                    <th style="padding: 8px; text-align: left; border-bottom: 2px solid #dee2e6;">Document</th>
                    <th style="padding: 8px; text-align: right; border-bottom: 2px solid #dee2e6;">Amount</th>
                    <th style="padding: 8px; text-align: right; border-bottom: 2px solid #dee2e6;">Z-Score</th>
                    <th style="padding: 8px; text-align: left; border-bottom: 2px solid #dee2e6;">Vendor</th>
                </tr>
            </thead>
            <tbody>
"""
            for outlier in result['outliers'][:5]:  # Show top 5
                html += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>{outlier['number']}</strong></td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #dee2e6;">${outlier['amount']:,.2f}</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #dee2e6;"><span style="color: #dc3545;">{outlier['z_score']}σ</span></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{outlier['vendor']}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += "</div>"
        return html
    
    def _format_statistics_result(self, result: Dict) -> str:
        """Format statistics result"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        response = f"📊 **Statistical Analysis: {result['document_type'].replace('_', ' ').title()}**\n\n"
        response += f"**Distribution:**\n"
        response += f"• Count: {result['count']} documents\n"
        response += f"• Total: ${result['total']:,.2f}\n"
        response += f"• Mean: ${result['mean']:,.2f}\n"
        response += f"• Median: ${result['median']:,.2f}\n"
        response += f"• Std Dev: ${result['std_dev']:,.2f}\n\n"
        
        response += f"**Range:**\n"
        response += f"• Min: ${result['min']:,.2f}\n"
        response += f"• Max: ${result['max']:,.2f}\n\n"
        
        response += f"**Percentiles:**\n"
        response += f"• 25th: ${result['percentile_25']:,.2f}\n"
        response += f"• 50th: ${result['percentile_50']:,.2f}\n"
        response += f"• 75th: ${result['percentile_75']:,.2f}\n"
        response += f"• 95th: ${result['percentile_95']:,.2f}\n"
        
        return response
    
    def _format_trends_result(self, result: Dict) -> str:
        """Format trends result"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        response = f"📈 **Spending Trends by {result['group_by'].title()}**\n\n"
        response += f"**Top {len(result['trends'])} Categories:**\n\n"
        
        for i, trend in enumerate(result['trends'], 1):
            response += f"{i}. **{trend['category']}**\n"
            response += f"   💰 Total: ${trend['total']:,.2f}\n"
            response += f"   📋 Count: {trend['count']} documents\n"
            response += f"   💵 Average: ${trend['total']/trend['count']:,.2f}\n\n"
        
        return response
    
    def _format_risk_result(self, result: Dict) -> str:
        """Format risk assessment result"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        risk_icons = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }
        
        icon = risk_icons.get(result['risk_level'], "⚪")
        
        response = f"{icon} **Risk Assessment: {result['document_type']}**\n\n"
        response += f"**Document ID:** {result['document_id']}\n"
        response += f"**Risk Level:** {result['risk_level']}\n"
        response += f"**Risk Score:** {result['risk_score']}/10\n\n"
        
        if result['risk_factors']:
            response += f"**Risk Factors:**\n"
            for factor in result['risk_factors']:
                response += f"• {factor}\n"
            response += "\n"
        
        response += f"**Recommendation:**\n{result['recommendation']}"
        
        return response
    
    def _format_blocked_explanation(self, result: Dict) -> str:
        """Format blocked document explanation using KG reasoning"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        # If not blocked
        if not result.get('is_blocked', False):
            return f"ℹ️ {result.get('message', 'Document is not blocked')}"
        
        # Build comprehensive explanation
        html = f"""
<div style="background: white; padding: 20px; border-radius: 8px; border: 2px solid #dc3545;">
    <h5 style="color: #dc3545;">
        <i class="fas fa-ban"></i> Blocked Document Analysis
    </h5>
    
    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <div style="margin-bottom: 10px;"><strong>Document Type:</strong> {result['doc_type']}</div>
        <div style="margin-bottom: 10px;"><strong>Document ID:</strong> <code>{result['document_id']}</code></div>
        <div style="margin-bottom: 10px;"><strong>Status:</strong> <span style="color: #dc3545; font-weight: bold;">{result['status']}</span></div>
        <div style="margin-bottom: 10px;"><strong>Amount:</strong> ${result['amount']:,.2f}</div>
        <div><strong>Vendor:</strong> {result['vendor']}</div>
    </div>
    
    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 15px 0;">
        <strong>🔍 KG Reasoning Insight:</strong>
        <p style="margin: 10px 0 0 0;">{result['insight']}</p>
    </div>
    
    <h6 style="margin-top: 20px; color: #dc3545;">
        <i class="fas fa-exclamation-triangle"></i> Blocking Reasons:
    </h6>
    <div style="margin: 10px 0;">
"""
        
        for i, reason in enumerate(result.get('reasons', []), 1):
            severity_color = {
                'HIGH': '#dc3545',
                'MEDIUM': '#ffc107',
                'LOW': '#28a745'
            }.get(reason.get('severity', 'MEDIUM'), '#6c757d')
            
            html += f"""
        <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid {severity_color};">
            <div style="display: flex; justify-content: between; align-items: center;">
                <strong>{i}. {reason['category']}</strong>
                <span style="background: {severity_color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 10px;">
                    {reason.get('severity', 'MEDIUM')}
                </span>
            </div>
            <p style="margin: 8px 0 0 0;">{reason['description']}</p>
"""
            if 'factors' in reason and reason['factors']:
                html += """
            <div style="margin-top: 8px; font-size: 0.9em;">
                <strong>Contributing Factors:</strong>
                <ul style="margin: 5px 0 0 20px;">
"""
                for factor in reason['factors']:
                    html += f"<li>{factor}</li>"
                html += "</ul></div>"
            
            html += "</div>"
        
        html += """
    </div>
    
    <h6 style="margin-top: 20px; color: #0d6efd;">
        <i class="fas fa-lightbulb"></i> Recommended Actions:
    </h6>
    <ol style="margin: 10px 0;">
"""
        
        for rec in result.get('recommendations', []):
            html += f"<li style='margin-bottom: 8px;'>{rec}</li>"
        
        html += """
    </ol>
    
    <div style="background: #d1ecf1; padding: 12px; border-radius: 5px; border-left: 4px solid #0c5460; margin-top: 20px;">
        <strong>💡 Pro Tip:</strong> Visit the <a href="/knowledge-graph" target="_blank">Knowledge Graph</a> tab 
        to see visual relationships and get more context about this document's connections.
    </div>
</div>
"""
        
        return html
    
    def _init_openai(self):
        """Initialize OpenAI with function calling"""
        try:
            import openai
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                self.llm = openai
                print("✓ OpenAI with function calling enabled")
            else:
                print("⚠ OPENAI_API_KEY not set")
        except Exception as e:
            print(f"⚠ OpenAI not available: {e}")


def create_chatbot(workflow, llm_backend="none"):
    """Create tool-enhanced chatbot"""
    return P2PChatbotWithTools(workflow, llm_backend=llm_backend)
