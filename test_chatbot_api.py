"""
Testing API for P2P Chatbot
Allows programmatic testing of chatbot responses
"""
import requests
import json
from typing import Dict, List, Optional


class ChatbotTester:
    """
    Simple API client for testing the P2P chatbot
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.chat_url = f"{base_url}/api/chat"
    
    def ask(self, question: str) -> Dict:
        """
        Send a question to the chatbot and get the response
        
        Args:
            question: The question to ask
            
        Returns:
            Dict with 'message' containing the response
        """
        try:
            response = requests.post(
                self.chat_url,
                json={"message": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to connect to chatbot: {e}"
            }
    
    def test_questions(self, questions: List[str]) -> List[Dict]:
        """
        Test multiple questions and collect responses
        
        Args:
            questions: List of questions to test
            
        Returns:
            List of results with question and response
        """
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}/{len(questions)}: {question}")
            print('='*60)
            
            result = self.ask(question)
            
            # Check if response is HTML or plain text
            # API can return either 'message' or 'response' key
            message = result.get('message', result.get('response', ''))
            is_html = message.strip().startswith('<')
            
            results.append({
                'question': question,
                'response': result,
                'is_html': is_html,
                'length': len(message),
                'success': 'error' not in result
            })
            
            # Print summary
            if 'error' in result:
                print(f"❌ ERROR: {result['error']}")
            else:
                print(f"✅ Response received ({len(message)} chars)")
                if is_html:
                    print("📊 HTML visualization detected")
                    # Extract key info from HTML
                    if 'Blocked' in message or 'blocked' in message:
                        print("   → Blocked document analysis")
                    if 'Risk' in message or 'risk' in message:
                        print("   → Risk assessment")
                    if 'Outlier' in message or 'outlier' in message:
                        print("   → Outlier analysis")
                    if 'Trend' in message or 'trend' in message:
                        print("   → Spending trends")
                else:
                    # Show preview of plain text response
                    preview = message[:200].replace('\n', ' ')
                    if len(preview) > 0:
                        print(f"   {preview}...")
                    else:
                        print(f"   (Empty response)")
                        # Debug: print full result
                        print(f"   Full result: {result}")
        
        return results
    
    def print_summary(self, results: List[Dict]):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        html_responses = sum(1 for r in results if r['is_html'])
        
        print(f"Total Tests: {total}")
        print(f"Successful: {successful} ({successful/total*100:.0f}%)")
        print(f"Failed: {total - successful}")
        print(f"HTML Visualizations: {html_responses}")
        print(f"Plain Text: {total - html_responses}")
        
        # List failed tests
        failed = [r for r in results if not r['success']]
        if failed:
            print("\n❌ Failed Tests:")
            for r in failed:
                print(f"  - {r['question']}")
                print(f"    Error: {r['response'].get('error', 'Unknown')}")


def run_basic_tests():
    """Run basic chatbot tests"""
    print("🧪 P2P Chatbot Testing API")
    print("="*60)
    
    tester = ChatbotTester()
    
    # Test questions covering different features
    test_questions = [
        # Basic queries
        "show statistics",
        "help",
        
        # Document queries
        "show blocked documents",
        "show pending approvals",
        
        # KG Reasoning - Blocked documents
        "why is invoice INV-882C3B70 blocked?",
        
        # Tools - Outlier analysis
        "find outliers in invoices",
        
        # Tools - Spending trends
        "show spending trends by department",
        "show spending trends by month",
        
        # Tools - Risk assessment (need to find valid doc IDs from blocked list)
        # We'll ask about blocked docs first to get IDs
    ]
    
    results = tester.test_questions(test_questions)
    tester.print_summary(results)
    
    return results


def test_kg_reasoning():
    """Specifically test KG reasoning functionality"""
    print("\n🧠 Testing Knowledge Graph Reasoning")
    print("="*60)
    
    tester = ChatbotTester()
    
    # First get blocked documents
    print("\n1. Finding blocked documents...")
    result = tester.ask("show blocked documents")
    
    # Parse response to find blocked document IDs
    message = result.get('message', '')
    print(f"Response: {message[:200]}...")
    
    # Try to extract invoice ID from response
    import re
    invoice_match = re.search(r'INV-[A-F0-9]+', message)
    po_match = re.search(r'PO-[A-F0-9]+', message)
    
    invoice_id = invoice_match.group(0) if invoice_match else "INV-882C3B70"
    po_id = po_match.group(0) if po_match else "PO-47104425"
    
    print(f"\n   Found blocked invoice: {invoice_id}")
    if po_match:
        print(f"   Found blocked PO: {po_id}")
    
    # Test KG reasoning on specific documents
    kg_questions = [
        f"why is invoice {invoice_id} blocked?",
        f"explain invoice {invoice_id}",
        f"what is blocking {invoice_id}?",
    ]
    
    print("\n2. Testing KG reasoning queries...")
    results = tester.test_questions(kg_questions)
    
    # Check if KG reasoning is working
    kg_working = any(r['is_html'] and 'Blocking Reasons' in r['response'].get('message', '') 
                     for r in results)
    
    if kg_working:
        print("\n✅ Knowledge Graph Reasoning is working!")
    else:
        print("\n⚠️  Knowledge Graph Reasoning may not be working properly")
    
    return results


def test_tools():
    """Test analytical tools"""
    print("\n🔧 Testing Analytical Tools")
    print("="*60)
    
    tester = ChatbotTester()
    
    tool_questions = [
        "find outliers in invoices",
        "find outliers in purchase orders",
        "show spending trends by vendor",
        "show spending trends by department",
        "calculate detailed statistics for invoices",
    ]
    
    results = tester.test_questions(tool_questions)
    
    # Check if tools are working (should return HTML visualizations)
    tools_working = sum(1 for r in results if r['is_html']) > 0
    
    if tools_working:
        print(f"\n✅ Tools are working! ({sum(1 for r in results if r['is_html'])}/{len(results)} returned visualizations)")
    else:
        print("\n⚠️  Tools may not be working - no HTML visualizations detected")
    
    return results


def interactive_mode():
    """Interactive testing mode"""
    print("\n💬 Interactive Testing Mode")
    print("="*60)
    print("Type 'exit' or 'quit' to stop")
    print()
    
    tester = ChatbotTester()
    
    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            result = tester.ask(question)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                message = result['message']
                is_html = message.strip().startswith('<')
                
                if is_html:
                    print(f"\n📊 HTML Response ({len(message)} chars)")
                    print("   (View in browser at http://localhost:5000/chatbot)")
                    # Try to extract key info
                    if 'HIGH' in message:
                        print("   🔴 HIGH severity detected")
                    if 'MEDIUM' in message:
                        print("   🟡 MEDIUM severity detected")
                    if 'LOW' in message:
                        print("   🟢 LOW severity detected")
                else:
                    print(f"\nAssistant: {message}")
            
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_mode()
        elif sys.argv[1] == "kg":
            test_kg_reasoning()
        elif sys.argv[1] == "tools":
            test_tools()
        else:
            print("Usage: python test_chatbot_api.py [interactive|kg|tools]")
    else:
        # Run all tests
        print("\n🚀 Running All Tests\n")
        run_basic_tests()
        test_kg_reasoning()
        test_tools()
        
        print("\n" + "="*60)
        print("Testing complete! Run with 'interactive' for manual testing:")
        print("  python test_chatbot_api.py interactive")
        print("="*60)
