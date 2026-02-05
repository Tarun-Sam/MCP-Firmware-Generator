#!/usr/bin/env python3
"""
Ollama Sampling Server - Multi-turn code refinement
Phase 6: Optional enhancement
"""

import json
import os
from typing import Dict, List, Optional
import ollama
from pydantic import BaseModel

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class SamplingRequest(BaseModel):
    initial_prompt: str
    num_clarifying_questions: int = 3

class SamplingResponse(BaseModel):
    refined_prompt: str
    clarifying_questions: List[str]
    conversation_history: List[ConversationMessage]
    improved_requirements: str

class OllamaSamplingServer:
    """Generate clarifying questions for better code generation."""
    
    def __init__(self, host: str = None, model: str = None):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11435")
        self.model = model or os.getenv("OLLAMA_MODEL", "codellama")
        self.client = ollama.Client(host=self.host)
        self.conversation_history: List[Dict] = []
        
    def generate_clarifying_questions(self, description: str, num_questions: int = 3) -> List[str]:
        """Generate clarifying questions about the requirements."""
        
        prompt = f"""You are an embedded systems expert helping developers.
        
The user wants to build: {description}

Generate {num_questions} specific clarifying questions to better understand their requirements.
Questions should be about:
1. Sensor type and pins
2. Data transmission method
3. Power source
4. Display/UI needs
5. Timing/sampling requirements

Format: Return ONLY the questions, one per line, numbered 1-{num_questions}.
No explanations, just questions."""
        
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        
        questions_text = response['response']
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        return questions[:num_questions]
    
    def refine_requirements(self, initial_prompt: str, questions_and_answers: Dict[str, str]) -> str:
        """Refine requirements based on Q&A."""
        
        qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in questions_and_answers.items()])
        
        prompt = f"""Based on this initial request and clarification:

Initial Request: {initial_prompt}

Clarifications:
{qa_text}

Write a detailed, specific requirement for generating embedded system code.
Include all constraints, sensor types, protocols, and specifications.
Be precise and technical."""
        
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        
        return response['response']
    
    def suggest_algorithm(self, refined_requirements: str) -> Dict:
        """Suggest algorithm/approach for the code."""
        
        prompt = f"""Given these embedded system requirements:

{refined_requirements}

Suggest:
1. Overall algorithm/architecture
2. Key functions needed
3. Libraries required
4. Potential challenges
5. Optimization opportunities

Format as structured JSON."""
        
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        
        try:
            return json.loads(response['response'])
        except:
            return {"suggestion": response['response']}
    
    def generate_improved_prompt(self, 
                                initial_prompt: str,
                                refined_requirements: str) -> str:
        """Generate improved prompt for code generation."""
        
        prompt = f"""You are a code generation expert.

Original request: {initial_prompt}

Refined requirements: {refined_requirements}

Generate an improved, detailed prompt for an AI code generator.
The prompt should be specific, include:
- Exact pin assignments
- Library requirements
- Function signatures needed
- Code style preferences
- Error handling expectations

Make it detailed enough that any code generator would produce good code."""
        
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        
        return response['response']

# ============================================================================
# TEST MODE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Ollama Sampling Server - Multi-Turn Refinement Test")
    print("="*70 + "\n")
    
    server = OllamaSamplingServer()
    
    # Example: User wants WiFi temperature sensor
    initial_request = "WiFi temperature sensor with data logging"
    
    print(f"📝 Initial Request: {initial_request}\n")
    
    # Step 1: Generate clarifying questions
    print("❓ Generating clarifying questions...")
    questions = server.generate_clarifying_questions(initial_request, num_questions=3)
    
    print("\nClarifying Questions:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    
    # Step 2: Simulate user answers
    print("\n📋 Simulating user responses...")
    answers = {
        questions[0] if len(questions) > 0 else "Sensor type": "DHT22 on GPIO 23",
        questions[1] if len(questions) > 1 else "Cloud upload": "Upload to ThingSpeak",
        questions[2] if len(questions) > 2 else "Power source": "Mains powered, always on"
    }
    
    for q, a in answers.items():
        print(f"Q: {q}")
        print(f"A: {a}\n")
    
    # Step 3: Refine requirements
    print("🔧 Refining requirements...")
    refined = server.refine_requirements(initial_request, answers)
    print(f"\nRefined Requirements:\n{refined[:500]}...\n")
    
    # Step 4: Generate improved prompt
    print("✨ Generating improved code generation prompt...")
    improved_prompt = server.generate_improved_prompt(initial_request, refined)
    print(f"\nImproved Prompt:\n{improved_prompt[:500]}...\n")
    
    print("\n✓ Refinement complete!")
    print("="*70 + "\n")
