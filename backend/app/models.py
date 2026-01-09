from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    conversation_id: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]  # For MCQ
    correct_answer: str
    question_type: str  # "mcq" or "short_answer"
    topic: Optional[str] = None


class QuizRequest(BaseModel):
    num_questions: int = 5
    question_type: str = "mcq"  # "mcq" or "short_answer" or "mixed"
    topic: Optional[str] = None  # Optional topic filter


class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[QuizQuestion]
    created_at: datetime


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: Dict[int, str]  # question_index: answer


class QuizResult(BaseModel):
    quiz_id: str
    score: float
    total_questions: int
    correct_answers: int
    results: Dict[int, Dict[str, Any]]  # question_index: {correct, user_answer, correct_answer}


class ProgressResponse(BaseModel):
    total_quizzes: int
    total_questions_attempted: int
    average_score: float
    weak_areas: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


