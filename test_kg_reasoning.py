"""
Test script for Knowledge Graph Reasoning
Demonstrates fraud detection, risk assessment, and recommendations
"""
from workflow import P2PWorkflow
from sample_data import generate_sample_data
from kg_reasoning import P2PKnowledgeGraph
import json


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_fraud_patterns(patterns: list):
    """Print fraud detection results"""
    if not patterns:
        print("✓ No suspicious patterns detected")
        return
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern['type']} - Severity: {pattern['severity']}")
        print(f"   Vendor: {pattern['vendor']}")
        print(f"   Reason: {pattern['reason']}")
        if 'amount' in pattern:
            print(f"   Amount: ${pattern['amount']:,.2f}")
        if 'documents' in pattern:
            print(f"   Blocked Documents: {pattern['documents']}")


def print_vendor_risks(risks: dict):
    """Print vendor risk assessment"""
    if not risks:
        print("No vendor risk data available")
        return
    
    # Sort by risk score
    sorted_vendors = sorted(risks.items(), key=lambda x: x[1]['risk_score'], reverse=True)
    
    for vendor_id, risk_info in sorted_vendors:
        risk_level = risk_info['risk_level']
        emoji = "🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢"
        
        print(f"\n{emoji} {risk_info['vendor_name']}")
        print(f"   Risk Score: {risk_info['risk_score']} ({risk_level})")
        print(f"   Transactions: {risk_info['transaction_count']}")
        if risk_info['factors']:
            print("   Risk Factors:")
            for factor in risk_info['factors']:
                print(f"     • {factor}")


def print_recommendations(recommendations: list, category: str):
    """Print vendor recommendations"""
    if not recommendations:
        print(f"No vendors found for category: {category}")
        return
    
    print(f"\nTop vendors for {category}:")
    for i, rec in enumerate(recommendations[:5], 1):
        risk_emoji = "🟢" if rec['risk_level'] == "LOW" else "🟡" if rec['risk_level'] == "MEDIUM" else "🔴"
        print(f"\n{i}. {rec['vendor_name']} {risk_emoji}")
        print(f"   Avg Price: ${rec['avg_price']:.2f}")
        print(f"   Risk Level: {rec['risk_level']} (Score: {rec['risk_score']})")
        print(f"   Transactions: {rec['transaction_count']}")
        if rec['quality_issues'] > 0:
            print(f"   ⚠️  Quality Issues: {rec['quality_issues']}")


def print_three_way_match_issues(issues: list):
    """Print three-way match validation issues"""
    if not issues:
        print("✓ No three-way match issues detected")
        return
    
    for i, issue in enumerate(issues, 1):
        severity_emoji = "🔴" if issue['severity'] == "HIGH" else "🟡"
        print(f"\n{i}. {severity_emoji} {issue['issue']}")
        print(f"   Invoice: {issue['invoice_id']}")
        if 'variance_pct' in issue:
            print(f"   Variance: {issue['variance_pct']:.2f}%")


def print_approval_delays(predictions: list):
    """Print approval delay predictions"""
    if not predictions:
        print("✓ No documents at risk of approval delays")
        return
    
    for i, pred in enumerate(predictions, 1):
        risk_emoji = "🔴" if pred['risk_level'] == "HIGH" else "🟡"
        print(f"\n{i}. {risk_emoji} {pred['document_type']}: {pred['document_id']}")
        print(f"   Amount: ${pred['amount']:,.2f}")
        print(f"   Delay Risk: {pred['risk_level']} (Score: {pred['delay_risk_score']})")
        print(f"   Pending Approvers: {pred['pending_approvers']}")
        print("   Risk Factors:")
        for factor in pred['factors']:
            print(f"     • {factor}")


def print_consolidation_opportunities(opportunities: list):
    """Print vendor consolidation opportunities"""
    if not opportunities:
        print("No consolidation opportunities found")
        return
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['category']}")
        print(f"   Current Vendors: {opp['vendor_count']}")
        print(f"   Total Spend: ${opp['total_spend']:,.2f}")
        print(f"   💡 {opp['recommendation']}")
        print("\n   Vendor Breakdown:")
        for vendor_id, info in list(opp['vendors'].items())[:3]:
            print(f"     • {info['name']}: ${info['spend']:,.2f} ({info['transaction_count']} transactions)")


def main():
    """Run KG reasoning analysis"""
    print_section("P2P KNOWLEDGE GRAPH REASONING SYSTEM")
    print("\nInitializing system and generating sample data...")
    
    # Create workflow and generate data
    workflow = generate_sample_data()
    
    print(f"\n✓ Generated {len(workflow.purchase_orders)} POs, "
          f"{len(workflow.goods_receipts)} GRs, "
          f"{len(workflow.invoices)} invoices")
    
    # Build knowledge graph
    print("\nBuilding knowledge graph...")
    kg = P2PKnowledgeGraph()
    kg.build_graph_from_workflow(workflow)
    
    # Generate comprehensive report
    report = kg.generate_comprehensive_report(workflow)
    
    # Display results
    print_section("1. FRAUD DETECTION")
    print_fraud_patterns(report['fraud_patterns'])
    
    print_section("2. VENDOR RISK ASSESSMENT")
    print_vendor_risks(report['vendor_risks'])
    
    print_section("3. THREE-WAY MATCH VALIDATION")
    print_three_way_match_issues(report['three_way_match_issues'])
    
    print_section("4. APPROVAL DELAY PREDICTIONS")
    print_approval_delays(report['approval_delays'])
    
    print_section("5. VENDOR CONSOLIDATION OPPORTUNITIES")
    print_consolidation_opportunities(report['consolidation_opportunities'])
    
    print_section("6. VENDOR RECOMMENDATIONS BY CATEGORY")
    
    # Get recommendations for different categories
    categories = ['IT Equipment', 'Office Supplies', 'Manufacturing', 'Services']
    for category in categories:
        recommendations = kg.recommend_vendors(category, exclude_high_risk=True)
        if recommendations:
            print_recommendations(recommendations, category)
    
    print_section("7. GRAPH STATISTICS")
    stats = report['graph_stats']
    print(f"\n📊 Knowledge Graph Overview:")
    print(f"   • Total Nodes: {stats['total_nodes']}")
    print(f"   • Total Edges: {stats['total_edges']}")
    print(f"   • Vendors: {stats['total_vendors']}")
    print(f"   • Purchase Orders: {stats['total_pos']}")
    print(f"   • Invoices: {stats['total_invoices']}")
    
    print_section("SUMMARY")
    print("\n✓ Knowledge Graph Reasoning Analysis Complete")
    print("\nKey Insights:")
    fraud_count = len(report['fraud_patterns'])
    high_risk_vendors = sum(1 for v in report['vendor_risks'].values() 
                           if v['risk_level'] == 'HIGH')
    match_issues = len(report['three_way_match_issues'])
    delay_risks = len(report['approval_delays'])
    
    print(f"  • Fraud Patterns Detected: {fraud_count}")
    print(f"  • High-Risk Vendors: {high_risk_vendors}")
    print(f"  • Three-Way Match Issues: {match_issues}")
    print(f"  • Documents at Risk of Delays: {delay_risks}")
    
    print("\n" + "=" * 70)
    print("\n💡 The knowledge graph enables intelligent reasoning and predictions")
    print("   that would be difficult or impossible with traditional queries.\n")


if __name__ == "__main__":
    main()
