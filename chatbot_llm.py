"""
LLM-Enhanced chatbot for P2P workflow system
Uses OpenAI GPT for natural language understanding and generation
Falls back to rule-based system if API is unavailable
"""
import os
import json
from typing import Dict, Optional
from datetime import datetime
from chatbot import P2PChatbot


class P2PChatbotLLM(P2PChatbot):
    """
    Enhanced chatbot with LLM integration
    Extends the base rule-based chatbot with GPT capabilities
    """
    
    def __init__(self, workflow, api_key: Optional[str] = None):
        super().__init__(workflow)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.use_llm = bool(self.api_key)
        
        if self.use_llm:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = self.api_key
                print("✓ LLM integration enabled (OpenAI GPT)")
            except ImportError:
                print("⚠ OpenAI package not installed. Using rule-based system.")
                print("  Install with: pip install openai")
                self.use_llm = False
        else:
            print("ℹ No API key found. Using rule-based system.")
            print("  Set OPENAI_API_KEY environment variable to enable LLM.")
    
    def process_message(self, user_message: str) -> dict:
        """
        Process user message with LLM or fall back to rule-based system
        """
        # For specific queries that benefit most from structured data,
        # use rule-based system directly
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ['blocked', 'pending', 'stats', 'find', 'search']):
            # These queries need real-time data - use rule-based first
            rule_response = super().process_message(user_message)
            
            if self.use_llm:
                # Enhance the response with LLM for better presentation
                return self._enhance_with_llm(user_message, rule_response)
            return rule_response
        
        # For general questions, use LLM if available
        if self.use_llm:
            return self._process_with_llm(user_message)
        
        # Fall back to rule-based system
        return super().process_message(user_message)
    
    def _process_with_llm(self, user_message: str) -> dict:
        """
        Process message using LLM
        """
        try:
            # Build context from workflow data
            context = self._build_context()
            
            # Create system prompt
            system_prompt = f"""You are an AI assistant for a Purchase-to-Pay (P2P) workflow system. 

CURRENT SYSTEM STATE:
{context}

CAPABILITIES:
- Answer questions about the P2P process
- Explain procurement workflows
- Provide statistics and insights
- Analyze blocked documents with root cause analysis
- Guide users through approvals and processes

GUIDELINES:
- Be helpful, professional, and concise
- Use emojis sparingly for clarity
- Provide specific, actionable advice
- Reference actual data when available
- If you need specific real-time data, acknowledge the limitation

RESPONSE FORMAT:
- Use markdown formatting (**bold**, bullet points)
- Keep responses focused and scannable
- Provide step-by-step guidance when appropriate"""
            
            # Call OpenAI API
            response = self.openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            message = response.choices[0].message.content
            return {'message': message}
            
        except Exception as e:
            print(f"LLM error: {e}")
            print("Falling back to rule-based system")
            return super().process_message(user_message)
    
    def _enhance_with_llm(self, user_message: str, rule_response: dict) -> dict:
        """
        Enhance rule-based response with LLM for better presentation
        """
        try:
            system_prompt = """You are enhancing a P2P workflow response. 
The system has provided structured data. Your job is to:
1. Make the response more conversational and helpful
2. Add context and insights
3. Suggest next steps or related actions
4. Keep all the important data from the original response

Keep the response concise and actionable."""
            
            enhance_prompt = f"""User asked: "{user_message}"

System response:
{rule_response['message']}

Please enhance this response to be more helpful while keeping all the data."""
            
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Faster model for enhancements
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhance_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            enhanced_message = response.choices[0].message.content
            return {'message': enhanced_message, **rule_response}
            
        except Exception as e:
            print(f"Enhancement error: {e}")
            return rule_response
    
    def _build_context(self) -> str:
        """
        Build context summary from workflow data
        """
        stats = self.workflow.get_statistics()
        pending = self.workflow.get_all_pending_approvals()
        blocked = self.workflow.get_blocked_documents()
        
        context = f"""
Purchase Orders: {stats['total_pos']} (Approved: {stats['approved_pos']}, Pending: {stats['pending_pos']}, Blocked: {stats['blocked_pos']})
Goods Receipts: {stats['total_grs']} (Accepted: {stats['accepted_grs']}, Blocked: {stats['blocked_grs']})
Invoices: {stats['total_invoices']} (Paid: {stats['paid_invoices']}, Overdue: {stats['overdue_invoices']}, Blocked: {stats['blocked_invoices']})
Total Spend: ${stats['total_spend']:,.2f}

Pending Approvals: {len(pending['purchase_orders'])} POs, {len(pending['invoices'])} Invoices
Blocked Documents: {len(blocked['purchase_orders'])} POs, {len(blocked['goods_receipts'])} GRs, {len(blocked['invoices'])} Invoices

Approval Policies:
- Low Value ($0-$1,000): 1 approver
- Medium Value ($1,000-$10,000): 2 approvers
- High Value (>$10,000): 3 approvers
"""
        return context


# Wrapper function for easy testing without API key
def create_chatbot(workflow, use_llm=True):
    """
    Create appropriate chatbot based on availability
    """
    if use_llm:
        return P2PChatbotLLM(workflow)
    else:
        return P2PChatbot(workflow)
