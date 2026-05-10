"""
Groq API client with system prompts for all operations
"""
from groq import Groq
from config import settings
from typing import List, Dict
import json


class GroqClient:
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    async def summarize_document(self, context: str) -> Dict:
        """Summar

ize PDF content using Groq"""
        system_prompt = """You are an expert document summarizer. Analyze the provided PDF content and create a comprehensive summary that includes:
- Main topics and themes discussed
- Key concepts and their explanations
- Important facts, figures, or data points
- Overall structure and organization
- Learning objectives (if applicable)

Keep the summary educational, concise, and well-organized."""

        user_prompt = f"""Summarize the following document content:

{context[:4000]}  # Limit context length

Provide the summary in JSON format:
{{
  "overview": "Brief overview of the document",
  "main_topics": ["topic1", "topic2", ...],
  "key_concepts": ["concept1", "concept2", ...],
  "important_points": ["point1", "point2", ...]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            # Try to parse as JSON
            try:
                return json.loads(content)
            except:
                return {"overview": content}
        except Exception as e:
            print(f"Groq summarization error: {e}")
            return {"error": str(e)}
    
    async def generate_quiz(self, context: str, topic: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
        """Generate quiz questions using Groq with difficulty levels"""
        
        # Define difficulty parameters
        difficulty_guidelines = {
            "easy": """
- Questions should be straightforward and directly from the text
- Test basic recall and understanding
- Answers should be clearly stated in the document
- Focus on definitions, facts, and simple concepts""",
            "medium": """
- Questions require understanding and application
- Combine multiple concepts from the text
- Test comprehension beyond simple recall
- May require inference from provided information""",
            "hard": """
- Fully conceptual and analytical questions
- Require deep understanding and critical thinking
- Test ability to apply knowledge in new contexts
- May involve comparing, contrasting, or synthesizing concepts"""
        }
        
        diff_guide = difficulty_guidelines.get(difficulty.lower(), difficulty_guidelines["medium"])
        
        system_prompt = f"""You are an expert quiz creator. Generate {num_questions} multiple-choice questions at {difficulty.upper()} difficulty level.

DIFFICULTY GUIDELINES:{diff_guide}

Requirements:
- Questions must be based on factual information from the document
- Create 4 plausible options (A, B, C, D) for each question
- Ensure only ONE correct answer per question
- Provide brief explanations for the correct answers
- Tag each question with specific concept/topic it tests
- All questions should be at {difficulty.upper()} difficulty level

Return ONLY valid JSON array, no additional text."""

        user_prompt = f"""Based on this content about {topic}, create {num_questions} {difficulty.upper()} difficulty quiz questions:

{context[:3000]}

Format (JSON array):
[
  {{
    "id": 1,
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Brief explanation of why this is correct",
    "concept": "Specific concept/topic this question tests (e.g., 'supervised learning', 'data preprocessing')",
    "difficulty": "{difficulty}"
  }}
]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            try:
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                questions = json.loads(content.strip())
                return questions if isinstance(questions, list) else []
            except:
                print(f"Failed to parse quiz JSON: {content[:200]}")
                return []
        except Exception as e:
            print(f"Groq quiz generation error: {e}")
            return []
    
    async def answer_question(self, question: str, context_chunks: List[str]) -> Dict:
        """Answer question using  retrieved context"""
        system_prompt = """You are a helpful AI tutor. Answer the student's question using ONLY the provided context from their document.

Guidelines:
- Be accurate and cite specific parts of the context
- If the context doesn't contain the answer, say so clearly
- Keep answers educational and clear
- Reference specific sections when possible"""

        context = "\n\n".join([f"[Chunk {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])
        
        user_prompt = f"""Context from document:
{context[:3500]}

Student's Question: {question}

Provide your answer with citations."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            return {
                "answer": answer,
                "context_used": context_chunks
            }
        except Exception as e:
            print(f"Groq answer error: {e}")
            return {"error": str(e)}
    
    async def analyze_weaknesses(self, incorrect_answers: List[Dict]) -> List[str]:
        """Extract weak concepts from incorrect answers"""
        system_prompt = """You are an educational analyst. Analyze the student's incorrect quiz answers and extract key concepts they are struggling with.

Return a JSON array of weak concepts/keywords."""

        answers_text = "\n".join([
            f"Q: {ans.get('question', '')}\nIncorrect: {ans.get('user_answer', '')}\nCorrect: {ans.get('correct_answer', '')}"
            for ans in incorrect_answers
        ])
        
        user_prompt = f"""Analyze these incorrect answers:

{answers_text}

Extract weak concepts as JSON array: ["concept1", "concept2", ...]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                concepts = json.loads(content.strip())
                return concepts if isinstance(concepts, list) else []
            except:
                return []
        except Exception as e:
            print(f"Groq weakness analysis error: {e}")
            return []


# Singleton instance
groq_client = GroqClient()
