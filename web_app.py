"""
Flask web application for P2P workflow prototype
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from workflow import P2PWorkflow
from sample_data_large import generate_large_sample_data
from models import POStatus, GRStatus, InvoiceStatus
from chatbot_ultimate import P2PChatbotUltimate
from analytics_api import get_analytics_data
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'p2p_workflow_secret_key_2026'

# Initialize workflow with large sample data (50+ records)
workflow = generate_large_sample_data()

# Initialize ultimate chatbot: RAG + optional tools
# Default: RAG mode, tools disabled (can enable in settings)
# Using transformers LLM for better conversational responses
chatbot = P2PChatbotUltimate(workflow, llm_backend="transformers", tools_enabled=False)

# Initialize default configuration
app.config['CHATBOT_CONFIG'] = {
    'mode': 'rag',
    'llm_backend': 'transformers',
    'tools_enabled': False,
    'enabled_tools': [],
    'active_tools': []
}


@app.route('/')
def index():
    """Home page with dashboard"""
    stats = workflow.get_statistics()
    pending = workflow.get_all_pending_approvals()
    blocked = workflow.get_blocked_documents()
    
    return render_template('index.html', 
                          stats=stats,
                          pending_count=len(pending['purchase_orders']) + len(pending['invoices']),
                          blocked_count=len(blocked['purchase_orders']) + len(blocked['goods_receipts']) + len(blocked['invoices']))


@app.route('/purchase-orders')
def purchase_orders():
    """List all purchase orders"""
    pos = list(workflow.purchase_orders.values())
    return render_template('purchase_orders.html', purchase_orders=pos)


@app.route('/purchase-order/<po_id>')
def purchase_order_detail(po_id):
    """Show purchase order details"""
    summary = workflow.get_po_summary(po_id)
    if not summary:
        flash('Purchase order not found', 'error')
        return redirect(url_for('purchase_orders'))
    return render_template('po_detail.html', summary=summary)


@app.route('/goods-receipts')
def goods_receipts():
    """List all goods receipts"""
    grs = list(workflow.goods_receipts.values())
    return render_template('goods_receipts.html', goods_receipts=grs)


@app.route('/goods-receipt/<gr_id>')
def goods_receipt_detail(gr_id):
    """Show goods receipt details"""
    gr = workflow.goods_receipts.get(gr_id)
    if not gr:
        flash('Goods receipt not found', 'error')
        return redirect(url_for('goods_receipts'))
    return render_template('gr_detail.html', gr=gr)


@app.route('/invoices')
def invoices():
    """List all invoices"""
    invs = list(workflow.invoices.values())
    return render_template('invoices.html', invoices=invs)


@app.route('/invoice/<invoice_id>')
def invoice_detail(invoice_id):
    """Show invoice details"""
    invoice = workflow.invoices.get(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices'))
    return render_template('invoice_detail.html', invoice=invoice)


@app.route('/approval-policies')
def approval_policies():
    """Show approval policies"""
    policies = workflow.approval_policies
    return render_template('approval_policies.html', policies=policies)


@app.route('/pending-approvals')
def pending_approvals():
    """Show pending approvals"""
    pending = workflow.get_all_pending_approvals()
    return render_template('pending_approvals.html', pending=pending)


@app.route('/blocked-documents')
def blocked_documents():
    """Show blocked documents"""
    blocked = workflow.get_blocked_documents()
    return render_template('blocked_documents.html', blocked=blocked)


@app.route('/statistics')
def statistics():
    """Show workflow statistics"""
    stats = workflow.get_statistics()
    return render_template('statistics.html', stats=stats)


@app.route('/analytics')
def analytics_dashboard():
    """Show analytics dashboard with visualizations"""
    return render_template('analytics_dashboard.html')


@app.route('/api/analytics/data')
def api_analytics_data():
    """API endpoint for analytics data"""
    data = get_analytics_data(workflow)
    return jsonify(data)


@app.route('/knowledge-graph')
def knowledge_graph():
    """Show knowledge graph visualization"""
    return render_template('knowledge_graph.html')


@app.route('/api/knowledge-graph/data')
def api_knowledge_graph_data():
    """API endpoint for knowledge graph data"""
    from kg_reasoning import P2PKnowledgeGraph
    
    try:
        # Build knowledge graph
        kg = P2PKnowledgeGraph()
        kg.build_graph_from_workflow(workflow)
        
        # Convert graph to JSON format for visualization
        nodes = []
        edges = []
        
        # Add nodes with their properties
        for node_id, node_data in kg.graph.nodes(data=True):
            node_type = node_data.get('type', 'Unknown')
            node_name = node_data.get('name', node_id)
            
            # Determine node properties for visualization
            node_info = {
                'id': node_id,
                'label': node_name if len(node_name) < 30 else node_name[:27] + '...',
                'type': node_type,
                'group': node_type,
                'title': f"{node_type}: {node_name}",  # Tooltip
                'properties': {}
            }
            
            # Add relevant properties based on type
            if node_type == 'PurchaseOrder':
                node_info['properties'] = {
                    'amount': f"${node_data.get('amount', 0):,.2f}",
                    'status': node_data.get('status', 'Unknown'),
                    'blocked': node_data.get('blocked', False)
                }
            elif node_type == 'Invoice':
                node_info['properties'] = {
                    'amount': f"${node_data.get('amount', 0):,.2f}",
                    'status': node_data.get('status', 'Unknown'),
                    'blocked': node_data.get('blocked', False)
                }
            elif node_type == 'Vendor':
                node_info['properties'] = {
                    'risk_score': node_data.get('risk_score', 0),
                    'transaction_count': node_data.get('transaction_count', 0)
                }
            elif node_type == 'GoodsReceipt':
                node_info['properties'] = {
                    'status': node_data.get('status', 'Unknown'),
                    'quality_checked': node_data.get('quality_checked', False)
                }
            
            nodes.append(node_info)
        
        # Add edges with their relationships
        for source, target, edge_data in kg.graph.edges(data=True):
            relation = edge_data.get('relation', 'connected_to')
            edges.append({
                'from': source,
                'to': target,
                'label': relation,
                'title': relation,  # Tooltip
                'arrows': 'to'
            })
        
        # Get graph statistics
        stats = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'node_types': {}
        }
        
        # Count nodes by type
        for node in nodes:
            node_type = node['type']
            stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
        
        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge-graph/insights')
def api_knowledge_graph_insights():
    """API endpoint for knowledge graph insights"""
    from kg_reasoning import P2PKnowledgeGraph
    
    try:
        # Build knowledge graph
        kg = P2PKnowledgeGraph()
        kg.build_graph_from_workflow(workflow)
        
        # Generate comprehensive report
        report = kg.generate_comprehensive_report(workflow)
        
        # Format for JSON response
        response = {
            'fraud_patterns': report['fraud_patterns'],
            'vendor_risks': [
                {
                    'vendor_id': vid,
                    'vendor_name': data['vendor_name'],
                    'risk_score': data['risk_score'],
                    'risk_level': data['risk_level'],
                    'factors': data['factors'],
                    'transaction_count': data['transaction_count']
                }
                for vid, data in report['vendor_risks'].items()
            ],
            'three_way_match_issues': report['three_way_match_issues'],
            'approval_delays': report['approval_delays'],
            'consolidation_opportunities': report['consolidation_opportunities'],
            'graph_stats': report['graph_stats']
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/regenerate-data', methods=['POST'])
def regenerate_data():
    """Regenerate sample data"""
    global workflow
    workflow = generate_large_sample_data()
    flash('Sample data regenerated successfully! (50+ records)', 'success')
    return redirect(url_for('index'))


@app.route('/chatbot')
def chatbot_page():
    """Show chatbot interface"""
    return render_template('chatbot.html')


@app.route('/chatbot/settings')
def chatbot_settings():
    """Show chatbot configuration UI"""
    config = app.config.get('CHATBOT_CONFIG', {
        'mode': 'hybrid',
        'llm_backend': 'transformers',
        'tools_enabled': False,
        'enabled_tools': [],
        'active_tools': []
    })
    return render_template('chatbot_settings.html', config=config)


@app.route('/api/chatbot/configure', methods=['POST'])
def configure_chatbot():
    """Update chatbot configuration"""
    global chatbot
    
    # Get form data
    mode = request.form.get('mode', 'rule_based')
    llm_backend = request.form.get('llm_backend', 'none')
    
    # Get enabled tools (no master toggle needed)
    enabled_tools = []
    tool_mapping = {
        'tool_analyze_outliers': 'analyze_outliers',
        'tool_calculate_statistics': 'calculate_statistics',
        'tool_find_spending_trends': 'find_spending_trends',
        'tool_predict_payment_date': 'predict_payment_date',
        'tool_risk_assessment': 'risk_assessment'
    }
    for form_key, tool_name in tool_mapping.items():
        if request.form.get(form_key) == 'on':
            enabled_tools.append(tool_name)
    
    # Tools are enabled if any tool is checked
    tools_enabled = len(enabled_tools) > 0
    
    # Reinitialize chatbot - always use ultimate (RAG + optional tools)
    try:
        from chatbot_ultimate import P2PChatbotUltimate
        
        # Create ultimate chatbot with RAG + optional tools
        chatbot = P2PChatbotUltimate(
            workflow, 
            llm_backend=llm_backend,
            tools_enabled=tools_enabled
        )
        
        # Configure which tools are enabled
        if tools_enabled and enabled_tools:
            chatbot.enabled_tools = enabled_tools
        elif not tools_enabled:
            chatbot.enabled_tools = []  # Disable all tools
        
        # Save configuration
        app.config['CHATBOT_CONFIG'] = {
            'mode': mode,
            'llm_backend': llm_backend,
            'tools_enabled': tools_enabled,
            'enabled_tools': enabled_tools,
            'active_tools': enabled_tools if tools_enabled else []
        }
        
        flash(f'Chatbot reconfigured successfully! Mode: {mode}, Tools: {"Enabled" if tools_enabled else "Disabled"}', 'success')
    except Exception as e:
        flash(f'Error reconfiguring chatbot: {str(e)}', 'danger')
    
    return redirect(url_for('chatbot_settings'))


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chatbot"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please provide a message.'})
    
    response = chatbot.process_message(user_message)
    
    # Debug: Check response
    response_text = response['message']
    print(f"[API] Response length: {len(response_text)} chars")
    print(f"[API] Starts with HTML: {response_text.strip().startswith('<')}")
    if len(response_text) > 100:
        print(f"[API] First 100 chars: {response_text[:100]}")
    
    return jsonify({'response': response_text})


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    stats = workflow.get_statistics()
    return jsonify(stats)


# Template filters
@app.template_filter('format_datetime')
def format_datetime(value):
    """Format datetime for display"""
    if value is None:
        return 'N/A'
    return value.strftime('%Y-%m-%d %H:%M')


@app.template_filter('format_date')
def format_date(value):
    """Format date for display"""
    if value is None:
        return 'N/A'
    return value.strftime('%Y-%m-%d')


@app.template_filter('format_currency')
def format_currency(value):
    """Format currency for display"""
    return f"${value:,.2f}"


@app.template_filter('status_badge_class')
def status_badge_class(status):
    """Get CSS class for status badge"""
    status_str = status.value if hasattr(status, 'value') else str(status)
    
    status_map = {
        'Draft': 'secondary',
        'Pending Approval': 'warning',
        'Approved': 'success',
        'Rejected': 'danger',
        'In Progress': 'info',
        'Completed': 'success',
        'Cancelled': 'secondary',
        'Blocked': 'danger',
        'Received': 'info',
        'Quality Check': 'info',
        'Accepted': 'success',
        'Paid': 'success',
        'Overdue': 'danger'
    }
    
    return status_map.get(status_str, 'secondary')


if __name__ == '__main__':
    import os
    
    # Get port from environment variable (Cloud Foundry) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*80)
    print("PURCHASE-TO-PAY WORKFLOW WEB APPLICATION")
    print("="*80)
    print("\nStarting Flask web server...")
    print(f"Port: {port}")
    print("="*80 + "\n")
    
    # Disable debug mode in production
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
