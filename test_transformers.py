"""
Test script to verify Transformers chatbot
"""
from workflow import P2PWorkflow
from sample_data_large import generate_large_sample_data
from chatbot_transformers import P2PChatbotTransformers

# Generate sample data
print("Generating sample data...")
workflow = generate_large_sample_data()

# Initialize chatbot
print("\nInitializing Transformers chatbot...")
chatbot = P2PChatbotTransformers(workflow)

# Test questions
print("\n" + "="*80)
print("TESTING TRANSFORMERS CHATBOT")
print("="*80)

questions = [
    "What is purchase to pay?",
    "Which invoices are blocked?",  # Should use rule-based
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
