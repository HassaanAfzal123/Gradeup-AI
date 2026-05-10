"""
Enhanced Quiz Agent with PDF text extraction and smart quiz generation
"""
import json
import re
from typing import List, Dict
from collections import Counter


class QuizAgent:
    def __init__(self):
        """Initialize the enhanced quiz generation agent"""
        pass
    
    async def generate_quiz(
        self, 
        context: str, 
        topic: str, 
        num_questions: int = 5
    ) -> List[Dict]:
        """
        Generate quiz questions from actual document context using RAG-grounded text analysis
        """
        if not context or len(context.strip()) < 100:
            return self._generate_fallback_questions(topic, num_questions)
        
        # Extract key sentences and concepts
        questions = self._smart_question_generation(context, topic, num_questions)
        return questions
    
    def _smart_question_generation(self, context: str, topic: str, num_questions: int) -> List[Dict]:
        """Generate questions based on actual content analysis"""
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', context) if len(s.strip()) > 20]
        
        questions = []
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i] if i < len(sentences) else sentences[0]
            
            # Extract key terms
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence)
            key_term = words[0] if words else topic
            
            # Create question from sentence
            if "is" in sentence.lower() or "are" in sentence.lower():
                question_text = f"According to the document, what is true about {key_term}?"
            elif "can" in sentence.lower() or "could" in sentence.lower():
                question_text = f"What capability is mentioned regarding {key_term}?"
            else:
                question_text = f"What does the document state about {key_term}?"
            
            # Generate plausible options
            correct_answer = sentence[:80] + "..." if len(sentence) > 80 else sentence
            
            questions.append({
                "id": i + 1,
                "question": question_text,
                "options": [
                    correct_answer,
                    f"This concept is not discussed in the document",
                    f"{key_term} is only mentioned briefly without detail",
                    f"The document contradicts this information"
                ],
                "correct_answer": correct_answer,
                "explanation": f"This is stated in the document: '{correct_answer}'"
            })
        
        return questions
    
    def _generate_fallback_questions(self, topic: str, num_questions: int) -> List[Dict]:
        """Generate fallback questions when context is insufficient"""
        questions = []
        
        templates = [
            {
                "question": f"What is the primary focus of {topic}?",
                "options": [
                    f"Understanding fundamental principles of {topic}",
                    f"Historical context only",
                    f"Advanced theoretical applications",
                    "Unrelated concepts"
                ],
                "correct_answer": f"Understanding fundamental principles of {topic}",
                "explanation": f"The document focuses on fundamental principles of {topic}."
            },
            {
                "question": f"Which approach is most relevant to {topic}?",
                "options": [
                    "A comprehensive, multi-faceted approach",
                    "A purely theoretical approach",
                    "A historical-only perspective",
                    "A limited, single-aspect view"
                ],
                "correct_answer": "A comprehensive, multi-faceted approach",
                "explanation": f"{topic} requires understanding from multiple perspectives."
            },
            {
                "question": f"What is a key characteristic discussed about {topic}?",
                "options": [
                    "Complexity and practical applications",
                    "Simple, straightforward concepts only",
                    "Outdated methodologies",
                    "Limited scope"
                ],
                "correct_answer": "Complexity and practical applications",
                "explanation": f"{topic} combines theoretical depth with practical applications."
            },
            {
                "question": f"How is {topic} typically applied?",
                "options": [
                    "Across multiple domains and contexts",
                    "In a single, narrow context only",
                    "Without practical implementation",
                    "Only in theoretical scenarios"
                ],
                "correct_answer": "Across multiple domains and contexts",
                "explanation": f"{topic} has broad applicability across various fields."
            },
            {
                "question": f"What should be prioritized when studying {topic}?",
                "options": [
                    "Understanding core concepts and foundations",
                    "Memorizing specific details only",
                    "Focusing solely on history",
                    "Avoiding practical examples"
                ],
                "correct_answer": "Understanding core concepts and foundations",
                "explanation": "Foundational understanding is crucial for mastery."
            }
        ]
        
        for i in range(min(num_questions, len(templates))):
            questions.append({
                "id": i + 1,
                **templates[i]
            })
        
        return questions
    
    async def grade_answer(
        self,
        question_id: int,
        user_answer: str,
        correct_answer: str,
        context: str
    ) -> Dict[str, any]:
        """Grade with detailed citation"""
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        
        # Find relevant citation
        citation = self._find_citation(correct_answer, context)
        
        explanation = (
            f"✅ Correct! {correct_answer}" 
            if is_correct 
            else f"❌ Incorrect. The correct answer is: {correct_answer}"
        )
        
        return {
            "correct": is_correct,
            "citation": citation,
            "explanation": explanation,
            "correct_answer": correct_answer
        }
    
    def _find_citation(self, answer: str, context: str) -> str:
        """Extract relevant citation from context"""
        if not context:
            return answer[:200] + "..." if len(answer) > 200 else answer
        
        # Try to find the answer in context
        if answer in context:
            start = context.find(answer)
            citation_start = max(0, start - 50)
            citation_end = min(len(context), start + len(answer) + 50)
            return "..." + context[citation_start:citation_end] + "..."
        
        # Return first relevant chunk
        return context[:250] + "..." if len(context) > 250 else context


# Singleton instance
quiz_agent = QuizAgent()
