"""
Ultimate P2P Chatbot: RAG + Optional Tools
Best of all worlds: Knowledge base + Optional advanced analysis
"""
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime
from chatbot_rag import P2PChatbotRAG


class P2PChatbotUltimate(P2PChatbotRAG):
    """
    Ultimate chatbot combining:
    1. Rule-based accuracy for P2P queries
    2. RAG (Retrieval-Augmented Generation) for context
    3. Optional advanced analytical tools
    """
    
    def __init__(self, workflow, llm_backend: str = "transformers", tools_enabled: bool = False):
        super().__init__(workflow, llm_backend=llm_backend)
        
        # Tool configuration
        self.tools_enabled = tools_enabled
        self.enabled_tools = []
        
        # Register tools
        self._register_tools()
        
        print(f"✓ Ultimate chatbot initialized")
        print(f"  Mode: RAG + {'Tools' if tools_enabled else 'No Tools'}")
        print(f"  LLM: {llm_backend}")
        if tools_enabled:
            print(f"  Available tools: {', '.join(self.enabled_tools)}")
    
    def _register_tools(self):
        """Register available analytical tools"""
        # Import tool functions from chatbot_tools
        self.tool_functions = {
            'analyze_outliers': self._tool_analyze_outliers,
            'calculate_statistics': self._tool_calculate_statistics,
            'find_spending_trends': self._tool_find_spending_trends,
            'predict_payment_date': self._tool_predict_payment_date,
            'risk_assessment': self._tool_risk_assessment
        }
        
        # All tools available by default
        self.enabled_tools = list(self.tool_functions.keys())
    
    def process_message(self, user_message: str) -> dict:
        """
        Process message: Try tools first (if enabled), check for blocked doc questions, then RAG/rule-based
        """
        message = user_message.lower().strip()
        
        # Check for blocked document explanation requests FIRST (before tools)
        if 'blocked' in message and ('why' in message or 'explain' in message or 'what' in message):
            # This is asking about blocked documents - use KG reasoning
            kg_response = self._handle_why_question(user_message)
            if kg_response and 'message' in kg_response:
                # Check if KG reasoning provided a good answer
                if not any(x in kg_response['message'] for x in ['not found', 'no blocked', 'not blocked']):
                    return kg_response
        
        # If tools are enabled, check if message requires a tool
        if self.tools_enabled:
            tool_response = self._try_tools(message)
            if tool_response:
                return tool_response
        
        # Fall back to RAG/rule-based processing
        return super().process_message(user_message)
    
    def _try_tools(self, message: str) -> Optional[dict]:
        """Try to handle message with tools"""
        
        # Check for blocked reason queries first (no tool needed, but special handling)
        if any(kw in message for kw in ['why', 'reason', 'cause']) and 'blocked' in message:
            # Extract document number if present
            words = message.split()
            for word in words:
                print(f"[DEBUG] Contains 'invoice': {'invoice' in message}")
                print(f"[DEBUG] Contains 'purchase order': {'purchase order' in message}")
                
                # Check for invoice first (more specific)
                if 'invoice' in message:
                    print(f"[DEBUG] → Analyzing INVOICES")
                    result = self._tool_analyze_outliers("invoices")
                    return {'message': self._format_outlier_result(result)}
                # Then check for PO (use word boundaries to avoid false matches)
                elif 'purchase order' in message or message.startswith('po ') or ' po ' in message or message.endswith(' po'):
                    print(f"[DEBUG] → Analyzing PURCHASE ORDERS")
                    result = self._tool_analyze_outliers("purchase_orders")
                    return {'message': self._format_outlier_result(result)}
                elif 'goods receipt' in message or 'gr' in message.split():
                    print(f"[DEBUG] → Analyzing GOODS RECEIPTS")
                    result = self._tool_analyze_outliers("goods_receipts")
                    return {'message': self._format_outlier_result(result)}
                # Default to invoices if unclear
                else:
                    print(f"[DEBUG] → Defaulting to INVOICES")
                    result = self._tool_analyze_outliers("invoices")
                    return {'message': self._format_outlier_result(result)}
        
        # Statistics calculation
        if 'calculate_statistics' in self.enabled_tools:
            if any(kw in message for kw in ['detailed stat', 'full stat', 'complete stat']):
                if 'po' in message or 'purchase order' in message:
                    result = self._tool_calculate_statistics("purchase_orders")
                    return {'message': self._format_statistics_result(result)}
                elif 'invoice' in message:
                    result = self._tool_calculate_statistics("invoices")
                    return {'message': self._format_statistics_result(result)}
        
        # Spending trends
        if 'find_spending_trends' in self.enabled_tools:
            if any(kw in message for kw in ['trend', 'spending pattern', 'spending history', 'spend by']):
                print(f"[DEBUG] Spending trend request detected. Message: '{message}'")
                if 'department' in message:
                    print(f"[DEBUG] → Analyzing by DEPARTMENT")
                    result = self._tool_find_spending_trends("department")
                    return {'message': self._format_trends_result(result)}
                elif 'vendor' in message:
                    print(f"[DEBUG] → Analyzing by VENDOR")
                    result = self._tool_find_spending_trends("vendor")
                    return {'message': self._format_trends_result(result)}
                elif 'month' in message or 'time' in message or 'history' in message:
                    print(f"[DEBUG] → Analyzing by MONTH")
                    result = self._tool_find_spending_trends("month")
                    return {'message': self._format_trends_result(result)}
                else:
                    # Default to month for general trend questions
                    print(f"[DEBUG] → Defaulting to MONTH analysis")
                    result = self._tool_find_spending_trends("month")
                    return {'message': self._format_trends_result(result)}
        
        # Risk assessment
        if 'risk_assessment' in self.enabled_tools:
            if 'risk' in message or 'assess' in message:
                words = message.split()
                for word in words:
                    if '-' in word:
                        result = self._tool_risk_assessment(word.upper())
                        return {'message': self._format_risk_result(result)}
        
        return None
    
    # ==================== TOOL IMPLEMENTATIONS ====================
    
    def _tool_analyze_outliers(self, document_type: str, threshold: float = 2.0) -> Dict:
        """Identify outliers using Z-score"""
        if document_type == "purchase_orders":
            documents = list(self.workflow.purchase_orders.values())
        elif document_type == "invoices":
            documents = list(self.workflow.invoices.values())
        elif document_type == "goods_receipts":
            documents = list(self.workflow.goods_receipts.values())
        else:
            return {"error": "Invalid document type"}
        
        amounts = [doc.total_amount for doc in documents]
        
        if len(amounts) < 3:
            return {"error": "Not enough data for outlier analysis"}
        
        mean = np.mean(amounts)
        std_dev = np.std(amounts)
        
        outliers = []
        for doc in documents:
            z_score = abs(doc.total_amount - mean) / std_dev if std_dev > 0 else 0
            
            if z_score > threshold:
                # Get correct document number based on type
                if document_type == "purchase_orders":
                    doc_number = doc.po_number
                elif document_type == "invoices":
                    doc_number = doc.invoice_number
                elif document_type == "goods_receipts":
                    doc_number = doc.gr_number
                else:
                    doc_number = "Unknown"
                
                outlier_info = {
                    "id": doc.id,
                    "number": doc_number,
                    "amount": doc.total_amount,
                    "z_score": round(z_score, 2),
                    "deviation_from_mean": round(doc.total_amount - mean, 2),
                    "vendor": getattr(doc, 'vendor_name', 'N/A')
                }
                outliers.append(outlier_info)
        
        outliers.sort(key=lambda x: x['z_score'], reverse=True)
        
        return {
            "document_type": document_type,
            "total_documents": len(documents),
            "mean_amount": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "threshold": threshold,
            "outliers_found": len(outliers),
            "outliers": outliers[:10]
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
        
        trends = {}
        for po in pos:
            if group_by == "department":
                key = po.department
            elif group_by == "vendor":
                key = po.vendor_name
            elif group_by == "month":
                key = po.creation_date.strftime("%Y-%m")
            else:
                return {"error": "Invalid group_by parameter"}
            
            if key not in trends:
                trends[key] = {"count": 0, "total": 0}
            trends[key]["count"] += 1
            trends[key]["total"] += po.total_amount
        
        sorted_trends = sorted(
            [{"category": k, **v} for k, v in trends.items()],
            key=lambda x: x["total"],
            reverse=True
        )
        
        return {
            "group_by": group_by,
            "categories": len(sorted_trends),
            "trends": sorted_trends[:10]
        }
    
    def _tool_predict_payment_date(self, invoice_id: str) -> Dict:
        """Predict payment date"""
        invoice = self.workflow.invoices.get(invoice_id)
        
        if not invoice:
            return {"error": "Invoice not found"}
        
        if invoice.status.value == "Paid":
            return {
                "invoice_id": invoice_id,
                "status": "Already paid",
                "payment_date": invoice.payment_date.strftime("%Y-%m-%d") if invoice.payment_date else "N/A"
            }
        
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
        """Assess document risk"""
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
        
        risk_score = 0
        risk_factors = []
        
        if doc.total_amount > 50000:
            risk_score += 3
            risk_factors.append("High value transaction")
        elif doc.total_amount > 10000:
            risk_score += 1
            risk_factors.append("Medium value transaction")
        
        if hasattr(doc, 'status'):
            if doc.status.value == "Blocked":
                risk_score += 5
                risk_factors.append("Document is blocked")
            elif doc.status.value == "Pending Approval":
                risk_score += 2
                risk_factors.append("Awaiting approval")
        
        if doc_type == "Invoice" and hasattr(doc, 'due_date'):
            days_until_due = (doc.due_date - datetime.now()).days
            if days_until_due < 0:
                risk_score += 4
                risk_factors.append(f"Overdue by {abs(days_until_due)} days")
        
        if risk_score >= 7:
            risk_level = "CRITICAL"
        elif risk_score >= 4:
            risk_level = "HIGH"
        elif risk_score >= 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        recommendations = {
            "CRITICAL": "Immediate action required - escalate to management",
            "HIGH": "Priority attention needed - review within 24 hours",
            "MEDIUM": "Monitor closely - review within this week",
            "LOW": "Normal processing - standard workflow"
        }
        
        return {
            "document_id": document_id,
            "document_type": doc_type,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendation": recommendations.get(risk_level, "Review as needed")
        }
    
    # ==================== RESULT FORMATTING ====================
    
    def _format_outlier_result(self, result: Dict) -> str:
        """Format outlier analysis with CSS-based box plot visualization"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        # Get all documents for visualization
        doc_type = result['document_type']
        if doc_type == "purchase_orders":
            documents = list(self.workflow.purchase_orders.values())
        elif doc_type == "invoices":
            documents = list(self.workflow.invoices.values())
        else:
            documents = list(self.workflow.goods_receipts.values())
        
        amounts = sorted([doc.total_amount for doc in documents])
        mean = result['mean_amount']
        std_dev = result['std_dev']
        
        # Calculate quartiles for box plot
        import numpy as np
        q1 = np.percentile(amounts, 25)
        median = np.percentile(amounts, 50)
        q3 = np.percentile(amounts, 75)
        min_val = min(amounts)
        max_val = max(amounts)
        
        # Upper and lower bounds for outliers
        upper_bound = mean + (2 * std_dev)
        lower_bound = max(0, mean - (2 * std_dev))
        
        # Create HTML visualization
        doc_type_display = doc_type.replace('_', ' ').title()
        html = f"""
<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; max-width: 800px;">
    <h5 style="margin-top: 0;">📊 Outlier Analysis: {doc_type_display}</h5>
    
    <!-- Summary Cards -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0;">
        <div style="background: #e3f2fd; padding: 12px; border-radius: 6px; text-align: center;">
            <div style="font-size: 24px; font-weight: bold; color: #1976d2;">{result['total_documents']}</div>
            <div style="font-size: 11px; color: #666;">Total Documents</div>
        </div>
        <div style="background: #ffebee; padding: 12px; border-radius: 6px; text-align: center;">
            <div style="font-size: 24px; font-weight: bold; color: #d32f2f;">{result['outliers_found']}</div>
            <div style="font-size: 11px; color: #666;">Outliers Found</div>
        </div>
        <div style="background: #e8f5e9; padding: 12px; border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #388e3c;">${mean:,.0f}</div>
            <div style="font-size: 11px; color: #666;">Mean Amount</div>
        </div>
        <div style="background: #fff3e0; padding: 12px; border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #f57c00;">${std_dev:,.0f}</div>
            <div style="font-size: 11px; color: #666;">Std Deviation</div>
        </div>
    </div>
    
    <!-- Box Plot Visualization -->
    <div style="margin: 30px 0;">
        <h6 style="margin-bottom: 15px;">📦 Distribution Box Plot</h6>
        <div style="position: relative; height: 120px; background: #f8f9fa; border-radius: 4px; padding: 20px;">
            <!-- Scale line -->
            <div style="position: absolute; top: 60px; left: 20px; right: 20px; height: 2px; background: #dee2e6;"></div>
            
            <!-- Min marker -->
            <div style="position: absolute; top: 50px; left: 20px;">
                <div style="width: 2px; height: 20px; background: #666; margin: 0 auto;"></div>
                <div style="font-size: 10px; margin-top: 5px; white-space: nowrap;">${min_val:,.0f}</div>
            </div>
            
            <!-- Box (Q1 to Q3) -->
            <div style="position: absolute; top: 45px; left: calc(20px + {((q1-min_val)/(max_val-min_val)*100 if max_val>min_val else 0)}%); width: {((q3-q1)/(max_val-min_val)*100 if max_val>min_val else 20)}%; height: 30px; background: #90caf9; border: 2px solid #1976d2; border-radius: 4px;">
                <!-- Median line -->
                <div style="position: absolute; left: {((median-q1)/(q3-q1)*100 if q3>q1 else 50)}%; top: 0; bottom: 0; width: 3px; background: #d32f2f;"></div>
            </div>
            
            <!-- Q1 label -->
            <div style="position: absolute; top: 80px; left: calc(20px + {((q1-min_val)/(max_val-min_val)*100 if max_val>min_val else 0)}%); font-size: 10px; transform: translateX(-50%);">
                Q1<br>${q1:,.0f}
            </div>
            
            <!-- Median label -->
            <div style="position: absolute; top: 25px; left: calc(20px + {((median-min_val)/(max_val-min_val)*100 if max_val>min_val else 10)}%); font-size: 10px; transform: translateX(-50%); color: #d32f2f; font-weight: bold;">
                Median<br>${median:,.0f}
            </div>
            
            <!-- Q3 label -->
            <div style="position: absolute; top: 80px; left: calc(20px + {((q3-min_val)/(max_val-min_val)*100 if max_val>min_val else 20)}%); font-size: 10px; transform: translateX(-50%);">
                Q3<br>${q3:,.0f}
            </div>
            
            <!-- Max marker -->
            <div style="position: absolute; top: 50px; right: 20px;">
                <div style="width: 2px; height: 20px; background: #666; margin: 0 auto;"></div>
                <div style="font-size: 10px; margin-top: 5px; white-space: nowrap;">${max_val:,.0f}</div>
            </div>
            
            <!-- Outlier threshold lines -->
            <div style="position: absolute; top: 35px; left: calc(20px + {((upper_bound-min_val)/(max_val-min_val)*100 if max_val>min_val else 80)}%); width: 2px; height: 50px; background: #ff5722; border-left: 2px dashed #ff5722;"></div>
            <div style="position: absolute; top: 20px; left: calc(20px + {((upper_bound-min_val)/(max_val-min_val)*100 if max_val>min_val else 80)}%); font-size: 9px; color: #ff5722; white-space: nowrap; transform: translateX(-50%);">
                +2σ
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 11px; color: #666;">
            <span style="color: #1976d2;">█</span> Normal Range (Q1-Q3) &nbsp;
            <span style="color: #d32f2f;">│</span> Median &nbsp;
            <span style="color: #ff5722;">┊</span> Outlier Threshold (±2σ)
        </div>
    </div>
"""
        
        # Add outlier details
        if result['outliers_found'] > 0:
            html += """
    <div style="margin-top: 25px;">
        <h6>⚠️ Detected Outliers (Top 5)</h6>
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0;">
"""
            for i, outlier in enumerate(result['outliers'][:5], 1):
                html += f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #ffe082;">
                <div style="flex: 1;">
                    <strong style="color: #f57c00;">{i}. {outlier['number']}</strong>
                    <span style="font-size: 12px; color: #666;"> - {outlier['vendor']}</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">${outlier['amount']:,.2f}</div>
                    <div style="font-size: 11px; color: #f57c00;">{outlier['z_score']}σ from mean</div>
                </div>
            </div>
"""
            html += """
        </div>
    </div>
"""
        else:
            html += """
    <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <strong style="color: #155724;">✅ No Outliers Detected!</strong><br>
        <span style="font-size: 13px; color: #155724;">All documents are within the normal range (±2 standard deviations from mean).</span>
    </div>
"""
        
        html += "</div>"
        return html
    
    def _format_statistics_result(self, result: Dict) -> str:
        """Format statistics"""
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
        """Format trends with visual line/bar chart"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        import json
        import uuid
        
        chart_id = f"chart-{uuid.uuid4().hex[:8]}"
        group_by = result['group_by']
        
        # Prepare data for chart
        categories = [trend['category'] for trend in result['trends']]
        totals = [trend['total'] for trend in result['trends']]
        counts = [trend['count'] for trend in result['trends']]
        
        # Determine chart type based on grouping
        if group_by == "month":
            chart_type = "line"  # Time series = line chart
            x_label = "Time Period"
        else:
            chart_type = "bar"  # Categories = bar chart
            x_label = group_by.title()
        
        html = f"""
<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; max-width: 800px;">
    <h5 style="margin-top: 0;">📈 Spending Trends by {group_by.title()}</h5>
    
    <!-- Summary Cards -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0;">
        <div style="background: #e3f2fd; padding: 12px; border-radius: 6px; text-align: center;">
            <div style="font-size: 24px; font-weight: bold; color: #1976d2;">{len(categories)}</div>
            <div style="font-size: 11px; color: #666;">Categories</div>
        </div>
        <div style="background: #e8f5e9; padding: 12px; border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #388e3c;">${sum(totals):,.0f}</div>
            <div style="font-size: 11px; color: #666;">Total Spend</div>
        </div>
        <div style="background: #fff3e0; padding: 12px; border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #f57c00;">${sum(totals)/len(totals):,.0f}</div>
            <div style="font-size: 11px; color: #666;">Average per Category</div>
        </div>
    </div>
    
    <!-- Chart -->
    <div style="margin: 25px 0;">
        <h6 style="margin-bottom: 15px;">Spending Trend Chart</h6>
        <canvas id="{chart_id}" style="max-height: 350px;"></canvas>
    </div>
    
    <script>
    (function() {{
        const ctx = document.getElementById('{chart_id}').getContext('2d');
        new Chart(ctx, {{
            type: '{chart_type}',
            data: {{
                labels: {json.dumps(categories)},
                datasets: [
                    {{
                        label: 'Total Spend ($)',
                        data: {json.dumps(totals)},
                        backgroundColor: '{("rgba(25, 118, 210, 0.2)" if chart_type == "line" else "rgba(25, 118, 210, 0.6)")}',
                        borderColor: 'rgba(25, 118, 210, 1)',
                        borderWidth: 2,
                        {'fill: true,' if chart_type == 'line' else ''}
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: '{x_label}'
                        }},
                        grid: {{
                            display: false
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Amount ($)'
                        }},
                        beginAtZero: true,
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
                                return 'Total: $' + context.parsed.y.toLocaleString();
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
    
    <!-- Top Categories Table -->
    <div style="margin-top: 25px;">
        <h6>Top {min(len(result['trends']), 10)} {group_by.title()}s</h6>
        <table style="width: 100%; font-size: 0.9em; border-collapse: collapse;">
            <thead style="background: #f8f9fa;">
                <tr>
                    <th style="padding: 8px; text-align: left; border-bottom: 2px solid #dee2e6;">#</th>
                    <th style="padding: 8px; text-align: left; border-bottom: 2px solid #dee2e6;">{group_by.title()}</th>
                    <th style="padding: 8px; text-align: right; border-bottom: 2px solid #dee2e6;">Total</th>
                    <th style="padding: 8px; text-align: center; border-bottom: 2px solid #dee2e6;">Count</th>
                    <th style="padding: 8px; text-align: right; border-bottom: 2px solid #dee2e6;">Average</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for i, trend in enumerate(result['trends'][:10], 1):
            avg = trend['total'] / trend['count']
            html += f"""
                <tr style="{'background: #f8f9fa;' if i % 2 == 0 else ''}">
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{i}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>{trend['category']}</strong></td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #dee2e6; color: #1976d2; font-weight: bold;">${trend['total']:,.2f}</td>
                    <td style="padding: 8px; text-align: center; border-bottom: 1px solid #dee2e6;">{trend['count']}</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #dee2e6;">${avg:,.2f}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</div>
"""
        
        return html
    
    def _handle_why_question(self, message: str) -> dict:
        """Override to use KG reasoning for blocked documents"""
        from chatbot_tools import P2PChatbotWithTools
        
        # Check if asking about blocked documents
        if 'blocked' in message.lower():
            # Extract document ID
            words = message.split()
            doc_id = None
            
            for word in words:
                word_upper = word.upper()
                # Look for document IDs (they contain hyphens)
                if '-' in word or any(prefix in word_upper for prefix in ['INV-', 'PO-', 'GR-', 'INV', 'PO', 'GR']):
                    # Try to find the exact document
                    # Check invoices
                    for inv in self.workflow.invoices.values():
                        if word_upper in inv.invoice_number or word_upper in inv.id:
                            doc_id = inv.id
                            break
                    if doc_id:
                        break
                    
                    # Check POs
                    for po in self.workflow.purchase_orders.values():
                        if word_upper in po.po_number or word_upper in po.id:
                            doc_id = po.id
                            break
                    if doc_id:
                        break
                    
                    # Check GRs
                    for gr in self.workflow.goods_receipts.values():
                        if word_upper in gr.gr_number or word_upper in gr.id:
                            doc_id = gr.id
                            break
                    if doc_id:
                        break
            
            # If we found a document ID, use KG reasoning tool
            if doc_id:
                # Create temporary tool chatbot to access the explain function
                tool_bot = P2PChatbotWithTools(self.workflow)
                result = tool_bot._tool_explain_blocked_document(doc_id)
                return {'message': tool_bot._format_blocked_explanation(result)}
            else:
                # No specific document found, show all blocked documents
                blocked = self.workflow.get_blocked_documents()
                if any(blocked.values()):
                    response = "🚫 **Blocked Documents Found:**\n\n"
                    
                    if blocked['invoices']:
                        response += f"**Invoices ({len(blocked['invoices'])}):**\n"
                        for inv in blocked['invoices'][:3]:
                            response += f"• {inv.invoice_number} - {inv.vendor_name} (${inv.total_amount:,.2f})\n"
                        response += "\n"
                    
                    if blocked['purchase_orders']:
                        response += f"**Purchase Orders ({len(blocked['purchase_orders'])}):**\n"
                        for po in blocked['purchase_orders'][:3]:
                            response += f"• {po.po_number} - {po.vendor_name} (${po.total_amount:,.2f})\n"
                        response += "\n"
                    
                    if blocked['goods_receipts']:
                        response += f"**Goods Receipts ({len(blocked['goods_receipts'])}):**\n"
                        for gr in blocked['goods_receipts'][:3]:
                            response += f"• {gr.gr_number} (${gr.total_amount:,.2f})\n"
                        response += "\n"
                    
                    response += "\n💡 **Tip:** Ask about a specific document for detailed KG reasoning analysis.\n"
                    response += "Example: 'Why is invoice INV-961D6D8D blocked?'"
                    return {'message': response}
                else:
                    return {'message': "✅ No blocked documents found in the system."}
        
        # If not asking about blocked, fall back to parent's search
        return super()._handle_why_question(message)
    
    def _format_blocked_invoice_analysis(self, inv) -> str:
        """Format blocked invoice analysis with rich HTML"""
        # Get related PO for analysis
        po = self.workflow.purchase_orders.get(inv.po_id)
        
        html = f"""
<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; max-width: 800px;">
    <h5 style="margin-top: 0;">🚫 Why is {inv.invoice_number} Blocked?</h5>
    
    <!-- Document Info Card -->
    <div style="background: #ffebee; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #d32f2f;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Invoice Number</div>
                <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">{inv.invoice_number}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Vendor</div>
                <div style="font-size: 16px; font-weight: bold; color: #333;">{inv.vendor_name}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Amount</div>
                <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">${inv.total_amount:,.2f}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Status</div>
                <div style="font-size: 16px; font-weight: bold; color: #d32f2f;">{inv.status.value}</div>
            </div>
        </div>
    </div>
    
    <!-- Blocked Reason -->
    <div style="background: #fff3cd; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #ffc107;">
        <h6 style="margin-top: 0; color: #856404;">🚫 Blocked Reason</h6>
        <p style="margin: 0; font-size: 14px; color: #856404;"><strong>{inv.blocked_reason}</strong></p>
    </div>
    
    <!-- Root Cause Analysis -->
    <div style="margin: 20px 0;">
        <h6>📊 Root Cause Analysis</h6>
"""
        
        # Analyze based on blocked reason
        if "pricing" in inv.blocked_reason.lower() or "price" in inv.blocked_reason.lower():
            if po:
                po_total = po.total_amount
                inv_total = inv.total_amount
                diff = abs(po_total - inv_total)
                variance = (diff / po_total * 100) if po_total > 0 else 0
                
                severity_color = "#d32f2f" if variance > 10 else "#f57c00" if variance > 5 else "#fbc02d"
                severity_label = "HIGH" if variance > 10 else "MEDIUM" if variance > 5 else "LOW"
                
                html += f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
            <strong style="color: #d32f2f;">💰 Price Discrepancy Detected</strong>
            <div style="margin-top: 10px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                <div style="background: white; padding: 10px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">PO Amount</div>
                    <div style="font-size: 18px; font-weight: bold; color: #1976d2;">${po_total:,.2f}</div>
                </div>
                <div style="background: white; padding: 10px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">Invoice Amount</div>
                    <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">${inv_total:,.2f}</div>
                </div>
                <div style="background: white; padding: 10px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">Variance</div>
                    <div style="font-size: 18px; font-weight: bold; color: {severity_color};">{variance:.1f}%</div>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 10px; background: {'#ffebee' if variance > 10 else '#fff3e0' if variance > 5 else '#fffde7'}; border-radius: 4px;">
                <strong style="color: {severity_color};">Severity: {severity_label}</strong>
                <div style="font-size: 13px; color: #666; margin-top: 5px;">
                    {f'Variance exceeds 10% tolerance - immediate attention required' if variance > 10 else f'Variance exceeds 5% tolerance - review needed' if variance > 5 else 'Minor variance detected'}
                </div>
            </div>
        </div>
"""
        
        elif "three-way" in inv.blocked_reason.lower() or "matching" in inv.blocked_reason.lower():
            html += f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
            <strong style="color: #d32f2f;">🔗 Three-Way Matching Failure</strong>
            <div style="margin-top: 15px;">
                <div style="margin: 10px 0; padding: 10px; background: white; border-radius: 4px; border-left: 3px solid #1976d2;">
                    <strong>1. Purchase Order:</strong> {inv.po_number}
                </div>
                <div style="margin: 10px 0; padding: 10px; background: white; border-radius: 4px; border-left: 3px solid #388e3c;">
                    <strong>2. Goods Receipt:</strong> {inv.gr_number}
                </div>
                <div style="margin: 10px 0; padding: 10px; background: white; border-radius: 4px; border-left: 3px solid #d32f2f;">
                    <strong>3. Invoice:</strong> {inv.invoice_number}
                </div>
            </div>
        </div>
"""
        
        # Action Required Section
        html += """
        <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; border-left: 4px solid #1976d2; margin-top: 15px;">
            <h6 style="margin-top: 0; color: #1976d2;">✅ Action Required</h6>
            <ul style="margin: 0; padding-left: 20px; color: #1565c0;">
"""
        
        if "pricing" in inv.blocked_reason.lower() or "price" in inv.blocked_reason.lower():
            html += """
                <li style="margin: 8px 0;">Validate invoice line items against Purchase Order</li>
                <li style="margin: 8px 0;">Contact vendor for corrected invoice or approve variance</li>
                <li style="margin: 8px 0;"><strong>Contact:</strong> Accounts Payable and vendor</li>
"""
        elif "three-way" in inv.blocked_reason.lower():
            html += """
                <li style="margin: 8px 0;">Verify all documents match (PO, GR, Invoice)</li>
                <li style="margin: 8px 0;">Reconcile discrepancies between documents</li>
                <li style="margin: 8px 0;"><strong>Contact:</strong> Procurement, Warehouse, and AP teams</li>
"""
        else:
            html += """
                <li style="margin: 8px 0;">Investigate and resolve blocking issue</li>
                <li style="margin: 8px 0;">Review invoice details and unblock</li>
                <li style="margin: 8px 0;"><strong>Contact:</strong> Accounts Payable manager</li>
"""
        
        html += """
            </ul>
        </div>
"""
        
        # Urgency indicator if due date approaching
        if inv.due_date:
            from datetime import datetime
            now = datetime.now()
            days_until_due = (inv.due_date - now).days
            
            if days_until_due < 0:
                html += f"""
        <div style="background: #d32f2f; color: white; padding: 15px; border-radius: 6px; margin-top: 15px; text-align: center;">
            <strong style="font-size: 16px;">⚠️ URGENT: Invoice is {abs(days_until_due)} days overdue!</strong>
            <div style="font-size: 13px; margin-top: 5px;">Immediate action required to avoid penalties</div>
        </div>
"""
            elif days_until_due < 7:
                html += f"""
        <div style="background: #f57c00; color: white; padding: 15px; border-radius: 6px; margin-top: 15px; text-align: center;">
            <strong style="font-size: 16px;">⚡ Priority: Invoice due in {days_until_due} days</strong>
            <div style="font-size: 13px; margin-top: 5px;">Please expedite resolution</div>
        </div>
"""
        
        html += """
    </div>
</div>
"""
        
        return html
    
    def _format_blocked_po_analysis(self, po) -> str:
        """Format blocked PO analysis with rich HTML"""
        html = f"""
<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; max-width: 800px;">
    <h5 style="margin-top: 0;">🚫 Why is {po.po_number} Blocked?</h5>
    
    <div style="background: #ffebee; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #d32f2f;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <div style="font-size: 11px; color: #666;">PO Number</div>
                <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">{po.po_number}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666;">Vendor</div>
                <div style="font-size: 16px; font-weight: bold;">{po.vendor_name}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666;">Amount</div>
                <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">${po.total_amount:,.2f}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666;">Blocked Reason</div>
                <div style="font-size: 14px; font-weight: bold; color: #856404;">{po.blocked_reason}</div>
            </div>
        </div>
    </div>
    
    <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; margin-top: 15px;">
        <h6 style="margin-top: 0;">✅ Action Required</h6>
        <p style="margin: 0;">Review and resolve blocking issue. Contact department manager or procurement team.</p>
    </div>
</div>
"""
        return html
    
    def _format_blocked_gr_analysis(self, gr) -> str:
        """Format blocked GR analysis with rich HTML"""
        html = f"""
<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; max-width: 800px;">
    <h5 style="margin-top: 0;">🚫 Why is {gr.gr_number} Blocked?</h5>
    
    <div style="background: #ffebee; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #d32f2f;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <div style="font-size: 11px; color: #666;">GR Number</div>
                <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">{gr.gr_number}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666;">Related PO</div>
                <div style="font-size: 16px; font-weight: bold;">{gr.po_number}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666;">Amount</div>
                <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">${gr.total_amount:,.2f}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666;">Blocked Reason</div>
                <div style="font-size: 14px; font-weight: bold; color: #856404;">{gr.blocked_reason}</div>
            </div>
        </div>
    </div>
    
    <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; margin-top: 15px;">
        <h6 style="margin-top: 0;">✅ Action Required</h6>
        <p style="margin: 0;">Investigate and resolve blocking issue. Contact warehouse manager or receiving team.</p>
    </div>
</div>
"""
        return html
    
    def _format_risk_result(self, result: Dict) -> str:
        """Format risk assessment with visual gauge"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        # Color coding based on risk level
        risk_colors = {
            "CRITICAL": "#d32f2f",
            "HIGH": "#f57c00",
            "MEDIUM": "#fbc02d",
            "LOW": "#388e3c"
        }
        
        risk_icons = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }
        
        color = risk_colors.get(result['risk_level'], "#9e9e9e")
        icon = risk_icons.get(result['risk_level'], "⚪")
        score = result['risk_score']
        max_score = 10
        percentage = (score / max_score) * 100
        
        html = f"""
<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; max-width: 700px;">
    <h5 style="margin-top: 0;">{icon} Risk Assessment: {result['document_type']}</h5>
    
    <!-- Document Info -->
    <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 15px 0;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Document ID</div>
                <div style="font-size: 16px; font-weight: bold; color: #333;">{result['document_id']}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Document Type</div>
                <div style="font-size: 16px; font-weight: bold; color: #333;">{result['document_type']}</div>
            </div>
        </div>
    </div>
    
    <!-- Risk Gauge -->
    <div style="margin: 25px 0;">
        <h6 style="margin-bottom: 15px;">Risk Score Gauge</h6>
        <div style="position: relative; height: 140px; background: #f8f9fa; border-radius: 8px; padding: 20px;">
            <!-- Risk level indicator -->
            <div style="position: absolute; top: 20px; left: 50%; transform: translateX(-50%); text-align: center;">
                <div style="font-size: 48px; font-weight: bold; color: {color};">{score}</div>
                <div style="font-size: 12px; color: #666;">out of {max_score}</div>
            </div>
            
            <!-- Risk bar -->
            <div style="position: absolute; bottom: 30px; left: 20px; right: 20px; height: 30px; background: #e0e0e0; border-radius: 15px; overflow: hidden;">
                <div style="height: 100%; width: {percentage}%; background: linear-gradient(90deg, #388e3c 0%, #fbc02d 50%, #f57c00 75%, #d32f2f 100%); transition: width 0.5s;"></div>
            </div>
            
            <!-- Risk labels -->
            <div style="position: absolute; bottom: 5px; left: 20px; right: 20px; display: flex; justify-content: space-between; font-size: 10px; color: #666;">
                <span>🟢 LOW</span>
                <span>🟡 MEDIUM</span>
                <span>🟠 HIGH</span>
                <span>🔴 CRITICAL</span>
            </div>
        </div>
        
        <!-- Risk Level Badge -->
        <div style="text-align: center; margin-top: 15px;">
            <div style="display: inline-block; background: {color}; color: white; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 16px;">
                {result['risk_level']} RISK
            </div>
        </div>
    </div>
"""
        
        # Risk Factors
        if result['risk_factors']:
            html += """
    <div style="margin: 25px 0;">
        <h6>⚠️ Risk Factors</h6>
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 4px;">
            <ul style="margin: 0; padding-left: 20px;">
"""
            for factor in result['risk_factors']:
                html += f"                <li style='margin: 8px 0; color: #856404;'>{factor}</li>\n"
            html += """
            </ul>
        </div>
    </div>
"""
        
        # Recommendation
        rec_colors = {
            "CRITICAL": "#ffebee",
            "HIGH": "#fff3e0",
            "MEDIUM": "#fffde7",
            "LOW": "#e8f5e9"
        }
        rec_border = {
            "CRITICAL": "#d32f2f",
            "HIGH": "#f57c00",
            "MEDIUM": "#fbc02d",
            "LOW": "#388e3c"
        }
        
        rec_bg = rec_colors.get(result['risk_level'], "#f5f5f5")
        rec_bdr = rec_border.get(result['risk_level'], "#9e9e9e")
        
        html += f"""
    <div style="margin: 25px 0;">
        <h6>💡 Recommendation</h6>
        <div style="background: {rec_bg}; border-left: 4px solid {rec_bdr}; padding: 15px; border-radius: 4px;">
            <strong style="color: #333;">{result['recommendation']}</strong>
        </div>
    </div>
</div>
"""
        
        return html


def create_chatbot(workflow, llm_backend="transformers", tools_enabled=False):
    """
    Create ultimate chatbot
    
    Default: RAG mode with optional tools
    """
    return P2PChatbotUltimate(workflow, llm_backend=llm_backend, tools_enabled=tools_enabled)
