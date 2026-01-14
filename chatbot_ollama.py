"""
Free LLM-Enhanced chatbot using Ollama (100% free, runs locally)
No API keys needed, complete privacy, unlimited usage
"""
import json
from typing import Dict, Optional
from datetime import datetime
from chatbot import P2PChatbot


class P2PChatbotOllama(P2PChatbot):
    """
    Enhanced chatbot with Ollama integration
    Uses free, local LLM models - no API keys or internet required
    Uses official Ollama Python library
    """
    
    def __init__(self, workflow, model: str = "llama2"):
        super().__init__(workflow)
        self.model = model
        self.use_llm = self._initialize_ollama()
        
        if self.use_llm:
            print(f"✓ Ollama integration enabled (Model: {self.model})")
            print(f"  Using ollama Python library")
        else:
            print("ℹ Ollama not available. Using rule-based system.")
            print("  Install with: pip install ollama")
            print("  Download Ollama: https://ollama.ai/download")
            print("  Then run: ollama pull llama2")
    
    def _initialize_ollama(self) -> bool:
        """Initialize Ollama client"""
        try:
            import ollama
            self.ollama = ollama
            # Try to list models to verify connection
            self.ollama.list()
            return True
        except ImportError:
            print("  Note: ollama package not installed")
            return False
        except Exception as e:
            print(f"  Note: Ollama service not running ({e})")
            return False
    
    def process_message(self, user_message: str) -> dict:
        """
        Process user message with Ollama or fall back to rule-based system
        """
        message_lower = user_message.lower()
        
        # For specific queries that need real-time data, use rule-based
        if any(keyword in message_lower for keyword in ['which', 'what', 'blocked', 'pending', 'stats', 'find']):
            rule_response = super().process_message(user_message)
            
            # If using LLM, enhance the response
            if self.use_llm and len(rule_response['message']) > 100:
                return self._enhance_with_ollama(user_message, rule_response)
            return rule_response
        
        # For general questions, use LLM if available
        if self.use_llm:
            return self._process_with_ollama(user_message)
        
        # Fall back to rule-based system
        return super().process_message(user_message)
    
    def _process_with_ollama(self, user_message: str) -> dict:
        """Process message using Ollama Python library"""
        try:
            context = self._build_context()
            
            prompt = f"""You are an AI assistant for a Purchase-to-Pay (P2P) workflow system.

CURRENT SYSTEM STATE:
{context}

USER QUESTION: {user_message}

Please provide a helpful, professional response. Use markdown formatting and keep it concise."""
            
            response = self.ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.7,
                }
            )
            
            message = response.get('response', '')
            return {'message': message}
                
        except Exception as e:
            print(f"Ollama error: {e}")
            return super().process_message(user_message)
    
    def _enhance_with_ollama(self, user_message: str, rule_response: dict) -> dict:
        """Enhance rule-based response with Ollama Python library"""
        try:
            prompt = f"""The user asked: "{user_message}"

Here's the data from the system:
{rule_response['message']}

Please make this response more conversational and add helpful insights while keeping all the important data. Keep it concise."""
            
            response = self.ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.7
                }
            )
            
            enhanced = response.get('response', '')
            return {'message': enhanced, **rule_response}
                
        except Exception as e:
            print(f"Enhancement error: {e}")
            return rule_response
    
    def _build_context(self) -> str:
        """Build context summary"""
        stats = self.workflow.get_statistics()
        pending = self.workflow.get_all_pending_approvals()
        blocked = self.workflow.get_blocked_documents()
        
        context = f"""Purchase Orders: {stats['total_pos']} (Approved: {stats['approved_pos']}, Pending: {stats['pending_pos']}, Blocked: {stats['blocked_pos']})
Goods Receipts: {stats['total_grs']} (Accepted: {stats['accepted_grs']}, Blocked: {stats['blocked_grs']})
Invoices: {stats['total_invoices']} (Paid: {stats['paid_invoices']}, Overdue: {stats['overdue_invoices']}, Blocked: {stats['blocked_invoices']})
Total Spend: ${stats['total_spend']:,.2f}

Pending Approvals: {len(pending['purchase_orders'])} POs, {len(pending['invoices'])} Invoices
Blocked Documents: {len(blocked['purchase_orders'])} POs, {len(blocked['goods_receipts'])} GRs, {len(blocked['invoices'])} Invoices"""
        
        return context


def create_chatbot(workflow, use_ollama=True):
    """Create chatbot with Ollama if available"""
    if use_ollama:
        return P2PChatbotOllama(workflow)
    else:
        return P2PChatbot(workflow)
