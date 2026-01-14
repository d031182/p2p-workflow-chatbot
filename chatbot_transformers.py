"""
100% Free LLM chatbot using Hugging Face Transformers
No API keys, no external services, completely free
Runs smaller models locally in pure Python
"""
from typing import Dict, Optional
from datetime import datetime
from chatbot import P2PChatbot


class P2PChatbotTransformers(P2PChatbot):
    """
    Enhanced chatbot with Hugging Face Transformers
    Uses free, local models - 100% free, pure Python
    """
    
    def __init__(self, workflow, model_name: str = "microsoft/DialoGPT-medium"):
        super().__init__(workflow)
        self.model_name = model_name
        self.use_llm = self._initialize_transformers()
        
        if self.use_llm:
            print(f"✓ Transformers integration enabled")
            print(f"  Model: {self.model_name}")
            print(f"  100% FREE - No API costs")
        else:
            print("ℹ Transformers not available. Using rule-based system.")
            print("  Install with: pip install transformers torch")
    
    def _initialize_transformers(self) -> bool:
        """Initialize Hugging Face Transformers"""
        try:
            from transformers import pipeline
            print("  Loading model (first time may take a minute)...")
            
            # Use a small, fast model for chatbot
            self.generator = pipeline(
                "text-generation",
                model="distilgpt2",  # Small, fast, free
                max_length=200,
                device=-1  # CPU (use 0 for GPU if available)
            )
            
            print("  Model loaded successfully!")
            return True
            
        except ImportError:
            print("  Note: transformers/torch not installed")
            return False
        except Exception as e:
            print(f"  Note: Could not load model ({e})")
            return False
    
    def process_message(self, user_message: str) -> dict:
        """
        Process user message with Transformers or fall back to rule-based system
        """
        message_lower = user_message.lower()
        
        # For specific data queries, use rule-based (more accurate for real-time data)
        # Only use rule-based if asking about specific documents/data
        if any(keyword in message_lower for keyword in ['which', 'blocked', 'pending', 'stats', 'find', 'show']) and not any(keyword in message_lower for keyword in ['what is', 'explain', 'tell me']):
            return super().process_message(user_message)
        
        # For general questions and explanations, try LLM first
        if self.use_llm:
            # Check if it's a question the rule-based system can handle well
            rule_response = super().process_message(user_message)
            
            # If rule-based gives a real answer (not the default "I'm not sure"), use it
            if "I'm not sure" not in rule_response['message']:
                return rule_response
            
            # Otherwise try Transformers
            return self._process_with_transformers(user_message)
        
        # Fall back to rule-based system
        return super().process_message(user_message)
    
    def _process_with_transformers(self, user_message: str) -> dict:
        """Process message using Transformers"""
        try:
            context = self._build_context()
            
            prompt = f"""P2P Workflow Assistant

System State:
{context}

User: {user_message}
Assistant:"""
            
            response = self.generator(
                prompt,
                max_length=len(prompt.split()) + 100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            # Extract just the assistant's response
            full_text = response[0]['generated_text']
            assistant_response = full_text.split("Assistant:")[-1].strip()
            
            return {'message': assistant_response}
                
        except Exception as e:
            print(f"Transformers error: {e}")
            return super().process_message(user_message)
    
    def _build_context(self) -> str:
        """Build context summary"""
        stats = self.workflow.get_statistics()
        
        context = f"""POs: {stats['total_pos']} (Approved: {stats['approved_pos']}, Pending: {stats['pending_pos']}, Blocked: {stats['blocked_pos']})
Invoices: {stats['total_invoices']} (Paid: {stats['paid_invoices']}, Overdue: {stats['overdue_invoices']})
Total Spend: ${stats['total_spend']:,.2f}"""
        
        return context


def create_chatbot(workflow):
    """Create chatbot with Transformers"""
    return P2PChatbotTransformers(workflow)
