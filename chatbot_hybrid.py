"""
Hybrid chatbot: Rule-based for accuracy + optional LLM for enhancement
100% free with Transformers, or use OpenAI/Ollama for better quality
"""
from typing import Dict, Optional
from datetime import datetime
from chatbot import P2PChatbot


class P2PChatbotHybrid(P2PChatbot):
    """
    Hybrid chatbot that:
    1. ALWAYS uses rule-based for getting accurate data
    2. Optionally enhances responses with LLM for better presentation
    """
    
    def __init__(self, workflow, llm_backend: str = "none"):
        """
        Initialize hybrid chatbot
        
        Args:
            workflow: P2P workflow instance
            llm_backend: "none", "transformers", "ollama", or "openai"
        """
        super().__init__(workflow)
        self.llm_backend = llm_backend
        self.llm = None
        
        if llm_backend == "transformers":
            self._init_transformers()
        elif llm_backend == "ollama":
            self._init_ollama()
        elif llm_backend == "openai":
            self._init_openai()
        else:
            print("✓ Using pure rule-based chatbot (recommended for P2P)")
            print("  100% FREE - Instant responses - Perfect accuracy")
    
    def _init_transformers(self):
        """Initialize Transformers"""
        try:
            from transformers import pipeline
            print("  Loading Transformers model...")
            self.llm = pipeline(
                "text2text-generation",
                model="google/flan-t5-small",  # Better for Q&A than distilgpt2
                max_length=512,
                device=-1
            )
            print("✓ Transformers LLM enabled (100% free)")
            print("  Model: google/flan-t5-small")
        except Exception as e:
            print(f"⚠ Transformers not available: {e}")
            print("  Using rule-based only")
    
    def _init_ollama(self):
        """Initialize Ollama"""
        try:
            import ollama
            self.llm = ollama
            ollama.list()  # Test connection
            print("✓ Ollama LLM enabled (100% free)")
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
                print("✓ OpenAI LLM enabled")
            else:
                print("⚠ OPENAI_API_KEY not set")
                print("  Using rule-based only")
        except Exception as e:
            print(f"⚠ OpenAI not available: {e}")
            print("  Using rule-based only")
    
    def process_message(self, user_message: str) -> dict:
        """
        Process message: Rule-based for data, optional LLM for enhancement
        """
        # ALWAYS get the rule-based response first (accurate data)
        rule_response = super().process_message(user_message)
        
        # If LLM is available and response is substantial, enhance it
        if self.llm and len(rule_response['message']) > 50:
            if self.llm_backend == "transformers":
                return self._enhance_with_transformers(user_message, rule_response)
            elif self.llm_backend == "ollama":
                return self._enhance_with_ollama(user_message, rule_response)
            elif self.llm_backend == "openai":
                return self._enhance_with_openai(user_message, rule_response)
        
        return rule_response
    
    def _enhance_with_transformers(self, question: str, rule_response: dict) -> dict:
        """Enhance with Transformers (100% free)"""
        try:
            # Use Flan-T5 for question answering
            context = rule_response['message']
            
            # Flan-T5 works with instructions
            prompt = f"""Make this response more conversational while keeping all the data:

Question: {question}

Data: {context}

Response:"""
            
            result = self.llm(prompt, max_length=512)
            enhanced = result[0]['generated_text']
            
            # If LLM response is too short or poor quality, use original
            if len(enhanced) < 50:
                return rule_response
            
            return {'message': enhanced, **rule_response}
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return rule_response
    
    def _enhance_with_ollama(self, question: str, rule_response: dict) -> dict:
        """Enhance with Ollama (100% free)"""
        try:
            prompt = f"""User asked: {question}

System data:
{rule_response['message']}

Make this more conversational while keeping ALL the data."""
            
            response = self.llm.generate(
                model="llama2",
                prompt=prompt,
                options={"temperature": 0.7}
            )
            
            return {'message': response['response'], **rule_response}
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return rule_response
    
    def _enhance_with_openai(self, question: str, rule_response: dict) -> dict:
        """Enhance with OpenAI"""
        try:
            response = self.llm.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Make responses more conversational while keeping all data."},
                    {"role": "user", "content": f"Question: {question}\n\nData: {rule_response['message']}"}
                ],
                temperature=0.7
            )
            
            return {'message': response.choices[0].message.content, **rule_response}
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return rule_response


def create_chatbot(workflow, llm_backend="none"):
    """
    Create hybrid chatbot
    
    llm_backend options:
    - "none": Pure rule-based (recommended, 100% free, instant)
    - "transformers": Free LLM (100% free, slower, requires pip install)
    - "ollama": Free LLM (100% free, requires Ollama app)
    - "openai": Paid LLM (best quality, requires API key)
    """
    return P2PChatbotHybrid(workflow, llm_backend=llm_backend)
