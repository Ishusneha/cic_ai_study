import os
from typing import List, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime
from .rag_pipeline import RAGPipeline

load_dotenv()


class QuizGenerator:
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.llm_model = os.getenv("LLM_MODEL", "llama3.2:latest")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.llm = ChatOllama(
            model=self.llm_model,
            temperature=0.7,
            base_url=self.ollama_base_url
        )
    
    def generate_quiz(
        self,
        num_questions: int = 5,
        question_type: str = "mcq",
        topic: str = None
    ) -> Dict[str, Any]:
        """Generate quiz questions from uploaded documents"""
        
        # Get relevant chunks
        if topic:
            query = f"Generate questions about: {topic}"
        else:
            query = "Generate comprehensive questions covering key concepts"
        
        chunks = self.rag_pipeline.get_relevant_chunks(query, k=15)
        
        if not chunks:
            raise ValueError("No documents available. Please upload study materials first.")
        
        # Combine chunk content
        context = "\n\n".join([chunk.page_content for chunk in chunks[:10]])
        
        # Generate questions based on type
        if question_type == "mcq":
            questions = self._generate_mcq(context, num_questions, topic)
        elif question_type == "short_answer":
            questions = self._generate_short_answer(context, num_questions, topic)
        else:  # mixed
            mcq_count = num_questions // 2
            sa_count = num_questions - mcq_count
            mcq_questions = self._generate_mcq(context, mcq_count, topic)
            sa_questions = self._generate_short_answer(context, sa_count, topic)
            questions = mcq_questions + sa_questions
        
        quiz_id = str(uuid.uuid4())
        
        return {
            "quiz_id": quiz_id,
            "questions": questions,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_mcq(self, context: str, num_questions: int, topic: str = None) -> List[Dict[str, Any]]:
        """Generate multiple choice questions"""
        topic_text = f" on the topic: {topic}" if topic else ""
        
        prompt_template = """You are an expert educator creating multiple choice questions for students.

Based on the following study material context, generate {num_questions} high-quality multiple choice questions{topic_text}.

Each question should:
1. Test understanding of key concepts
2. Have 4 options (A, B, C, D)
3. Have one clearly correct answer
4. Include plausible distractors
5. Be based strictly on the provided context

Context:
{context}

Generate the questions in the following JSON format:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "topic": "relevant topic or chapter"
    }}
  ]
}}

Return ONLY valid JSON, no additional text."""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format_messages(
            num_questions=num_questions,
            topic_text=topic_text,
            context=context[:8000]  # Limit context size
        )
        
        response = self.llm.invoke(formatted_prompt)
        content = response.content
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            questions = result.get("questions", [])
            
            # Format questions
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    "question": q["question"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "question_type": "mcq",
                    "topic": q.get("topic", topic or "General")
                })
            
            return formatted_questions[:num_questions]
        
        except json.JSONDecodeError as e:
            # Fallback: try to extract questions manually
            print(f"JSON parsing error: {e}")
            return self._fallback_mcq_generation(context, num_questions)
    
    def _generate_short_answer(self, context: str, num_questions: int, topic: str = None) -> List[Dict[str, Any]]:
        """Generate short answer questions"""
        topic_text = f" on the topic: {topic}" if topic else ""
        
        prompt_template = """You are an expert educator creating short answer questions for students.

Based on the following study material context, generate {num_questions} high-quality short answer questions{topic_text}.

Each question should:
1. Test understanding of key concepts
2. Require a brief but comprehensive answer (2-3 sentences)
3. Have a clear, specific correct answer
4. Be based strictly on the provided context

Context:
{context}

Generate the questions in the following JSON format:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "correct_answer": "The correct answer explanation",
      "topic": "relevant topic or chapter"
    }}
  ]
}}

Return ONLY valid JSON, no additional text."""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format_messages(
            num_questions=num_questions,
            topic_text=topic_text,
            context=context[:8000]
        )
        
        response = self.llm.invoke(formatted_prompt)
        content = response.content
        
        # Parse JSON response
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            questions = result.get("questions", [])
            
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    "question": q["question"],
                    "options": [],  # No options for short answer
                    "correct_answer": q["correct_answer"],
                    "question_type": "short_answer",
                    "topic": q.get("topic", topic or "General")
                })
            
            return formatted_questions[:num_questions]
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._fallback_short_answer_generation(context, num_questions)
    
    def _fallback_mcq_generation(self, context: str, num_questions: int) -> List[Dict[str, Any]]:
        """Fallback MCQ generation if JSON parsing fails"""
        # Simple fallback - create basic questions
        questions = []
        sentences = context.split(". ")[:num_questions * 2]
        
        for i, sentence in enumerate(sentences[:num_questions]):
            if len(sentence) > 50:
                questions.append({
                    "question": f"What is mentioned about: {sentence[:50]}...?",
                    "options": [
                        sentence[:100] if len(sentence) > 100 else sentence,
                        "Option B (incorrect)",
                        "Option C (incorrect)",
                        "Option D (incorrect)"
                    ],
                    "correct_answer": sentence[:100] if len(sentence) > 100 else sentence,
                    "question_type": "mcq",
                    "topic": "General"
                })
        
        return questions[:num_questions]
    
    def _fallback_short_answer_generation(self, context: str, num_questions: int) -> List[Dict[str, Any]]:
        """Fallback short answer generation if JSON parsing fails"""
        questions = []
        sentences = context.split(". ")[:num_questions * 2]
        
        for i, sentence in enumerate(sentences[:num_questions]):
            if len(sentence) > 50:
                questions.append({
                    "question": f"Explain: {sentence[:80]}...",
                    "options": [],
                    "correct_answer": sentence,
                    "question_type": "short_answer",
                    "topic": "General"
                })
        
        return questions[:num_questions]

