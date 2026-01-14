"""
Test outlier detection tool
"""
from workflow import P2PWorkflow
from sample_data_large import generate_large_sample_data
from chatbot_tools import P2PChatbotWithTools

# Generate sample data
print("Generating sample data...")
workflow = generate_large_sample_data()

# Initialize chatbot with tools
print("\nInitializing tool-enhanced chatbot...")
chatbot = P2PChatbotWithTools(workflow, llm_backend="none")

# Test questions
print("\n" + "="*80)
print("TESTING OUTLIER DETECTION TOOL")
print("="*80)

questions = [
    "Find outliers in invoices",
    "detect outliers in purchase orders",
    "analyze invoices for unusual amounts",
]

for question in questions:
    print(f"\nQuestion: {question}")
    print("-"*80)
    print("Response:")
    print("-"*80)
    
    response = chatbot.process_message(question)
    print(response['message'])
    print()

print("="*80)
print("TEST COMPLETE")
print("="*80)
