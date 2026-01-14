"""
Test approval policies question
"""
from workflow import P2PWorkflow
from sample_data_large import generate_large_sample_data
from chatbot import P2PChatbot

# Generate sample data
print("Generating sample data...")
workflow = generate_large_sample_data()

# Initialize chatbot
print("\nInitializing chatbot...")
chatbot = P2PChatbot(workflow)

# Test the question
print("\n" + "="*80)
print("TESTING: What are the approval policies?")
print("="*80)

question = "what are the approval policies?"
print(f"\nQuestion: {question}")
print("\n" + "-"*80)
print("Response:")
print("-"*80)

response = chatbot.process_message(question)
print(response['message'])

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
