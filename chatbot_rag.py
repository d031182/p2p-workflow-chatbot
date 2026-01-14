"""
RAG-Enhanced chatbot for P2P workflow
Uses knowledge base + LLM for accurate, context-aware responses
No training needed - just provide knowledge and let LLM reason!
"""
from typing import Dict, Optional
from datetime import datetime
from chatbot import P2PChatbot


class P2PChatbotRAG(P2PChatbot):
    """
    RAG (Retrieval-Augmented Generation) chatbot
    Combines rule-based accuracy with LLM reasoning
    """
    
    def __init__(self, workflow, llm_backend: str = "none"):
        super().__init__(workflow)
        self.llm_backend = llm_backend
        self.llm = None
        
        # Build knowledge base from workflow
        self.knowledge_base = self._build_knowledge_base()
        
        if llm_backend == "transformers":
            self._init_transformers()
        elif llm_backend == "ollama":
            self._init_ollama()
        elif llm_backend == "openai":
            self._init_openai()
        else:
            print("✓ Using rule-based with RAG knowledge base")
            print("  100% FREE - Answers questions about YOUR P2P system")
    
    def _build_knowledge_base(self) -> str:
        """
        Build knowledge base from actual workflow data
        This gives the LLM context about YOUR specific P2P system
        """
        kb = "# P2P WORKFLOW KNOWLEDGE BASE\n\n"
        
        # Approval Policies
        kb += "## APPROVAL POLICIES\n\n"
        for policy in self.workflow.approval_policies:
            kb += f"**{policy.name}**\n"
            kb += f"- Amount Range: ${policy.min_amount:,.2f} - ${policy.max_amount:,.2f}\n"
            kb += f"- Required Approvers: {', '.join(policy.required_approvers)}\n"
            kb += f"- Description: {policy.description}\n\n"
        
        # Current Statistics
        stats = self.workflow.get_statistics()
        kb += "## CURRENT SYSTEM STATUS\n\n"
        kb += f"- Total Purchase Orders: {stats['total_pos']}\n"
        kb += f"  - Approved: {stats['approved_pos']}\n"
        kb += f"  - Pending: {stats['pending_pos']}\n"
        kb += f"  - Blocked: {stats['blocked_pos']}\n"
        kb += f"- Total Goods Receipts: {stats['total_grs']}\n"
        kb += f"- Total Invoices: {stats['total_invoices']}\n"
        kb += f"- Total Spend: ${stats['total_spend']:,.2f}\n\n"
        
        # Process Explanation
        kb += "## P2P PROCESS FLOW\n\n"
        kb += "1. **Purchase Order (PO)** - Requester creates PO\n"
        kb += "2. **Approval** - Routed based on amount (see approval policies)\n"
        kb += "3. **Goods Receipt (GR)** - Warehouse records delivery\n"
        kb += "4. **Quality Check** - QA validates goods\n"
        kb += "5. **Invoice** - Vendor submits invoice\n"
        kb += "6. **Three-Way Match** - System matches PO + GR + Invoice\n"
        kb += "7. **Invoice Approval** - Finance approves payment\n"
        kb += "8. **Payment** - AP processes payment to vendor\n\n"
        
        # Blocked Documents
        blocked = self.workflow.get_blocked_documents()
        if len(blocked['invoices']) > 0 or len(blocked['purchase_orders']) > 0:
            kb += "## CURRENT BLOCKED DOCUMENTS\n\n"
            for inv in blocked['invoices']:
                kb += f"- Invoice {inv.invoice_number}: {inv.blocked_reason}\n"
            for po in blocked['purchase_orders']:
                kb += f"- PO {po.po_number}: {po.blocked_reason}\n"
            kb += "\n"
        
        return kb
    
    def _init_transformers(self):
        """Initialize Transformers with better Q&A model"""
        try:
            from transformers import pipeline
            print("  Loading Flan-T5 model (best free Q&A model)...")
            self.llm = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",  # Better than small, still free
                max_length=512,
                device=-1
            )
            print("✓ Transformers RAG enabled (100% free)")
            print("  Model: google/flan-t5-base (trained for Q&A)")
            print("  Knowledge base loaded from YOUR workflow")
        except Exception as e:
            print(f"⚠ Transformers not available: {e}")
            print("  Using rule-based only")
    
    def _init_ollama(self):
        """Initialize Ollama"""
        try:
            import ollama
            self.llm = ollama
            ollama.list()
            print("✓ Ollama RAG enabled (100% free)")
            print("  Knowledge base loaded from YOUR workflow")
        except Exception as e:
            print(f"⚠ Ollama not available: {e}")
            print("  Using rule-based only")
    
    def _init_openai(self):
        """Initialize OpenAI"""
        try:
            import openai
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                self.llm = openai
                print("✓ OpenAI RAG enabled")
                print("  Knowledge base loaded from YOUR workflow")
            else:
                print("⚠ OPENAI_API_KEY not set")
        except Exception as e:
            print(f"⚠ OpenAI not available: {e}")
    
    def process_message(self, user_message: str) -> dict:
        """
        Process with RAG: Retrieve relevant knowledge + Generate response
        """
        # If no LLM, use pure rule-based
        if not self.llm:
            return super().process_message(user_message)
        
        # Try rule-based first
        rule_response = super().process_message(user_message)
        
        # If rule-based has a good answer, check if it's HTML (visual reasoning)
        if "I'm not sure" not in rule_response['message']:
            # If response contains HTML formatting, return it as-is (don't enhance)
            if rule_response['message'].strip().startswith('<'):
                return rule_response
            
            # Rule-based worked with plain text, optionally enhance with LLM
            if len(rule_response['message']) > 100:
                return self._enhance_with_rag(user_message, rule_response)
            return rule_response
        
        # Rule-based couldn't answer, try LLM with knowledge base
        return self._answer_with_rag(user_message)
    
    def _answer_with_rag(self, question: str) -> dict:
        """Answer using RAG - LLM + Knowledge Base"""
        try:
            if self.llm_backend == "transformers":
                prompt = f"""Use this knowledge to answer the question:

{self.knowledge_base}

Question: {question}
Answer:"""
                
                result = self.llm(prompt, max_length=300)
                answer = result[0]['generated_text']
                return {'message': answer}
            
            elif self.llm_backend == "ollama":
                prompt = f"""Use this knowledge to answer accurately:

{self.knowledge_base}

Question: {question}"""
                
                response = self.llm.generate(
                    model="llama2",
                    prompt=prompt
                )
                return {'message': response['response']}
            
            elif self.llm_backend == "openai":
                response = self.llm.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a P2P assistant. Use this knowledge:\n{self.knowledge_base}"},
                        {"role": "user", "content": question}
                    ]
                )
                return {'message': response.choices[0].message.content}
        
        except Exception as e:
            print(f"RAG failed: {e}")
            return super().process_message(question)
    
    def _enhance_with_rag(self, question: str, rule_response: dict) -> dict:
        """Enhance rule response with RAG"""
        try:
            if self.llm_backend == "transformers":
                prompt = f"""Make this more conversational:

{rule_response['message']}"""
                
                result = self.llm(prompt, max_length=400)
                enhanced = result[0]['generated_text']
                
                if len(enhanced) > 50:
                    return {'message': enhanced, **rule_response}
                return rule_response
            
            # For Ollama/OpenAI, similar enhancement logic
            return rule_response
            
        except Exception as e:
            return rule_response


def create_chatbot(workflow, llm_backend="transformers"):
    """
    Create RAG chatbot with knowledge base
    
    llm_backend options:
    - "none": Pure rule-based
    - "transformers": Free LLM with RAG (recommended)
    - "ollama": Free LLM with RAG (better quality, needs Ollama)
    - "openai": Paid LLM with RAG (best quality)
    """
    return P2PChatbotRAG(workflow, llm_backend=llm_backend)
