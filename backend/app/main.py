from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import os
import uuid
from pathlib import Path
from datetime import datetime

from .models import (
    ChatRequest, ChatResponse, QuizRequest, QuizResponse,
    QuizSubmission, QuizResult, ProgressResponse
)
from .rag_pipeline import RAGPipeline
from .quiz_generator import QuizGenerator
from .progress_tracker import ProgressTracker

app = FastAPI(title="AI Study Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_pipeline = RAGPipeline()
quiz_generator = QuizGenerator(rag_pipeline)
progress_tracker = ProgressTracker()

# Create upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./backend/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Store conversation history (in production, use a database)
conversations = {}


@app.get("/")
async def root():
    return {"message": "AI Study Assistant API", "version": "1.0.0"}


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document (PDF, DOCX, TXT)"""
    try:
        # Validate file type
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ["pdf", "docx", "txt"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, DOCX, or TXT files."
            )
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}.{file_ext}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process and index document
        metadata = {
            "filename": file.filename,
            "uploaded_at": datetime.now().isoformat(),
            "file_id": file_id
        }
        
        chunks_count = rag_pipeline.process_and_index_documents(
            str(file_path),
            file_ext,
            metadata
        )
        
        return {
            "message": "Document uploaded and indexed successfully",
            "file_id": file_id,
            "filename": file.filename,
            "chunks_created": chunks_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI assistant"""
    try:
        # Get or create conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get answer from RAG pipeline
        result = rag_pipeline.answer_question(request.question)
        
        # Store in conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            "role": "user",
            "content": request.question,
            "timestamp": datetime.now().isoformat()
        })
        conversations[conversation_id].append({
            "role": "assistant",
            "content": result["answer"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Format sources as strings
        sources = []
        for source in result.get("sources", []):
            # Format source as a string with content and metadata
            content = source.get("content", "")
            metadata = source.get("metadata", {})
            if metadata:
                source_str = f"{content} [Source: {metadata.get('source', 'Unknown')}]"
            else:
                source_str = content
            sources.append(source_str)
        
        return ChatResponse(
            answer=result["answer"],
            sources=sources,
            conversation_id=conversation_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history")
async def get_chat_history(conversation_id: str):
    """Get chat history for a conversation"""
    if conversation_id not in conversations:
        return {"messages": []}
    
    return {"messages": conversations[conversation_id]}


@app.post("/api/quiz/generate", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate quiz questions from uploaded documents"""
    try:
        quiz_data = quiz_generator.generate_quiz(
            num_questions=request.num_questions,
            question_type=request.question_type,
            topic=request.topic
        )
        
        # Save quiz
        progress_tracker.save_quiz(quiz_data)
        
        return QuizResponse(
            quiz_id=quiz_data["quiz_id"],
            questions=quiz_data["questions"],
            created_at=datetime.fromisoformat(quiz_data["created_at"])
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    try:
        result = progress_tracker.submit_quiz(
            submission.quiz_id,
            submission.answers
        )
        
        return QuizResult(
            quiz_id=result["quiz_id"],
            score=result["score"],
            total_questions=result["total_questions"],
            correct_answers=result["correct_answers"],
            results=result["results"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quiz/history")
async def get_quiz_history():
    """Get quiz history"""
    try:
        history = progress_tracker.get_quiz_history()
        return {"quizzes": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/progress", response_model=ProgressResponse)
async def get_progress():
    """Get learning progress and analytics"""
    try:
        progress = progress_tracker.get_progress()
        return ProgressResponse(**progress)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/progress/weak-areas")
async def get_weak_areas():
    """Get identified weak areas"""
    try:
        progress = progress_tracker.get_progress()
        return {"weak_areas": progress["weak_areas"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


