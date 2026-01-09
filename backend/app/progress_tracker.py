import json
import os
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

class ProgressTracker:
    def __init__(self, storage_path: str = "./backend/progress_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.quizzes_file = self.storage_path / "quizzes.json"
        self.progress_file = self.storage_path / "progress.json"
        
        # Initialize files if they don't exist
        if not self.quizzes_file.exists():
            self._save_quizzes({})
        if not self.progress_file.exists():
            self._save_progress({})
    
    def _load_quizzes(self) -> Dict[str, Any]:
        """Load quiz data from file"""
        try:
            with open(self.quizzes_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_quizzes(self, data: Dict[str, Any]):
        """Save quiz data to file"""
        with open(self.quizzes_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load progress data from file"""
        try:
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_progress(self, data: Dict[str, Any]):
        """Save progress data to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_quiz(self, quiz_data: Dict[str, Any]):
        """Save a generated quiz"""
        quizzes = self._load_quizzes()
        quiz_id = quiz_data["quiz_id"]
        quizzes[quiz_id] = {
            **quiz_data,
            "submitted": False,
            "score": None
        }
        self._save_quizzes(quizzes)
    
    def submit_quiz(self, quiz_id: str, answers: Dict[int, str]) -> Dict[str, Any]:
        """Submit quiz answers and calculate score"""
        quizzes = self._load_quizzes()
        
        if quiz_id not in quizzes:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        quiz = quizzes[quiz_id]
        questions = quiz["questions"]
        
        correct_count = 0
        results = {}
        
        for idx, question in enumerate(questions):
            user_answer = answers.get(idx, "")
            correct_answer = question["correct_answer"]
            
            is_correct = False
            if question["question_type"] == "mcq":
                # For MCQ, compare exact match
                is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            else:
                # For short answer, use keyword matching (simplified)
                user_lower = user_answer.strip().lower()
                correct_lower = correct_answer.strip().lower()
                # Check if key terms match (simple approach)
                key_terms = [word for word in correct_lower.split() if len(word) > 4]
                matches = sum(1 for term in key_terms if term in user_lower)
                is_correct = matches >= len(key_terms) * 0.5  # 50% keyword match
            
            if is_correct:
                correct_count += 1
            
            results[idx] = {
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "question": question["question"],
                "topic": question.get("topic", "General")
            }
        
        score = (correct_count / len(questions)) * 100 if questions else 0
        
        # Update quiz
        quiz["submitted"] = True
        quiz["score"] = score
        quiz["answers"] = answers
        quiz["results"] = results
        quiz["submitted_at"] = datetime.now().isoformat()
        
        quizzes[quiz_id] = quiz
        self._save_quizzes(quizzes)
        
        # Update progress
        self._update_progress(quiz)
        
        return {
            "quiz_id": quiz_id,
            "score": score,
            "total_questions": len(questions),
            "correct_answers": correct_count,
            "results": results
        }
    
    def _update_progress(self, quiz: Dict[str, Any]):
        """Update overall progress statistics"""
        progress = self._load_progress()
        
        # Initialize if needed
        if "total_quizzes" not in progress:
            progress["total_quizzes"] = 0
        if "total_questions_attempted" not in progress:
            progress["total_questions_attempted"] = 0
        if "scores" not in progress:
            progress["scores"] = []
        if "topic_performance" not in progress:
            progress["topic_performance"] = {}
        if "recent_activity" not in progress:
            progress["recent_activity"] = []
        
        # Update statistics
        progress["total_quizzes"] += 1
        progress["total_questions_attempted"] += len(quiz["questions"])
        progress["scores"].append(quiz["score"])
        
        # Update topic performance
        for idx, result in quiz["results"].items():
            topic = result.get("topic", "General")
            if topic not in progress["topic_performance"]:
                progress["topic_performance"][topic] = {
                    "total": 0,
                    "correct": 0
                }
            progress["topic_performance"][topic]["total"] += 1
            if result["correct"]:
                progress["topic_performance"][topic]["correct"] += 1
        
        # Add recent activity
        progress["recent_activity"].append({
            "quiz_id": quiz["quiz_id"],
            "score": quiz["score"],
            "total_questions": len(quiz["questions"]),
            "timestamp": quiz.get("submitted_at", datetime.now().isoformat())
        })
        
        # Keep only last 20 activities
        progress["recent_activity"] = progress["recent_activity"][-20:]
        
        self._save_progress(progress)
    
    def get_progress(self) -> Dict[str, Any]:
        """Get overall progress statistics"""
        progress = self._load_progress()
        quizzes = self._load_quizzes()
        
        # Calculate average score
        scores = progress.get("scores", [])
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Identify weak areas (topics with < 70% accuracy)
        weak_areas = []
        topic_performance = progress.get("topic_performance", {})
        
        for topic, perf in topic_performance.items():
            accuracy = (perf["correct"] / perf["total"]) * 100 if perf["total"] > 0 else 0
            if accuracy < 70:
                weak_areas.append({
                    "topic": topic,
                    "accuracy": round(accuracy, 2),
                    "total_questions": perf["total"],
                    "correct_answers": perf["correct"]
                })
        
        # Sort weak areas by accuracy (lowest first)
        weak_areas.sort(key=lambda x: x["accuracy"])
        
        return {
            "total_quizzes": progress.get("total_quizzes", 0),
            "total_questions_attempted": progress.get("total_questions_attempted", 0),
            "average_score": round(average_score, 2),
            "weak_areas": weak_areas[:10],  # Top 10 weak areas
            "recent_activity": progress.get("recent_activity", [])[-10:]  # Last 10 activities
        }
    
    def get_quiz_history(self) -> List[Dict[str, Any]]:
        """Get all quiz history"""
        quizzes = self._load_quizzes()
        return [
            {
                "quiz_id": quiz_id,
                "created_at": quiz.get("created_at"),
                "submitted": quiz.get("submitted", False),
                "score": quiz.get("score"),
                "total_questions": len(quiz.get("questions", []))
            }
            for quiz_id, quiz in quizzes.items()
        ]


