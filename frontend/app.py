import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}


def make_api_request(endpoint: str, method: str = "GET", data: Dict = None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def upload_file(file):
    """Upload a file to the backend"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/api/upload", files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Upload Error: {str(e)}")
        return None


def main():
    st.title("📚 AI Study Assistant")
    st.markdown("Upload your study materials and get AI-powered help with understanding, practice, and revision!")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Document Upload")
        uploaded_file = st.file_uploader(
            "Upload PDF, DOCX, or TXT",
            type=["pdf", "docx", "txt"],
            help="Upload your syllabus, notes, or textbooks"
        )
        
        if uploaded_file is not None:
            if st.button("Upload Document"):
                with st.spinner("Uploading and processing document..."):
                    result = upload_file(uploaded_file)
                    if result:
                        st.success(f"✅ {result.get('filename')} uploaded successfully!")
                        st.info(f"📄 {result.get('chunks_created')} chunks created")
        
        st.divider()
        
        st.header("📊 Navigation")
        page = st.radio(
            "Choose a page",
            ["💬 Chat", "📝 Quiz", "📈 Progress"],
            index=0
        )
    
    # Main content based on selected page
    if page == "💬 Chat":
        show_chat_page()
    elif page == "📝 Quiz":
        show_quiz_page()
    elif page == "📈 Progress":
        show_progress_page()


def show_chat_page():
    st.header("💬 Chat with AI Assistant")
    st.markdown("Ask questions about your uploaded study materials")
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    if "sources" in message and message["sources"]:
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(message["sources"][:3]):
                                st.text(f"Source {i+1}: {source.get('content', '')[:200]}...")
    
    # Chat input
    user_question = st.chat_input("Ask a question about your study materials...")
    
    if user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Get conversation ID
        if not st.session_state.conversation_id:
            st.session_state.conversation_id = None
        
        # Get response from API
        with st.spinner("Thinking..."):
            response = make_api_request(
                "/api/chat",
                method="POST",
                data={
                    "question": user_question,
                    "conversation_id": st.session_state.conversation_id
                }
            )
        
        if response:
            st.session_state.conversation_id = response.get("conversation_id")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response.get("answer"),
                "sources": response.get("sources", [])
            })
            st.rerun()


def show_quiz_page():
    st.header("📝 Quiz Generator")
    st.markdown("Generate practice questions from your study materials")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Quiz generation form
        with st.form("quiz_form"):
            num_questions = st.slider("Number of Questions", 3, 20, 5)
            question_type = st.selectbox(
                "Question Type",
                ["mcq", "short_answer", "mixed"]
            )
            topic = st.text_input(
                "Topic (optional)",
                placeholder="e.g., Photosynthesis, Chapter 3, etc."
            )
            
            generate_btn = st.form_submit_button("Generate Quiz", type="primary")
        
        if generate_btn:
            with st.spinner("Generating quiz questions..."):
                response = make_api_request(
                    "/api/quiz/generate",
                    method="POST",
                    data={
                        "num_questions": num_questions,
                        "question_type": question_type,
                        "topic": topic if topic else None
                    }
                )
            
            if response:
                st.session_state.current_quiz = response
                st.session_state.quiz_answers = {}
                st.success("Quiz generated successfully!")
                st.rerun()
    
    with col2:
        st.subheader("Quiz History")
        history_response = make_api_request("/api/quiz/history")
        if history_response and history_response.get("quizzes"):
            for quiz in history_response["quizzes"][-5:]:
                score = quiz.get("score", "N/A")
                if score != "N/A":
                    score = f"{score:.1f}%"
                st.text(f"Quiz: {quiz['quiz_id'][:8]}...")
                st.text(f"Score: {score}")
                st.text(f"Questions: {quiz.get('total_questions', 0)}")
                st.divider()
    
    # Display current quiz
    if st.session_state.current_quiz:
        st.divider()
        st.subheader("Current Quiz")
        
        quiz = st.session_state.current_quiz
        questions = quiz.get("questions", [])
        
        # Quiz form
        with st.form("quiz_answers_form"):
            for idx, question in enumerate(questions):
                st.markdown(f"**Question {idx + 1}:** {question['question']}")
                
                if question["question_type"] == "mcq":
                    options = question.get("options", [])
                    selected = st.radio(
                        "Select an answer:",
                        options,
                        key=f"q_{idx}",
                        label_visibility="collapsed"
                    )
                    st.session_state.quiz_answers[idx] = selected
                else:
                    answer = st.text_area(
                        "Your answer:",
                        key=f"q_{idx}",
                        height=100
                    )
                    st.session_state.quiz_answers[idx] = answer
                
                st.divider()
            
            submit_btn = st.form_submit_button("Submit Quiz", type="primary")
        
        if submit_btn:
            with st.spinner("Evaluating your answers..."):
                response = make_api_request(
                    "/api/quiz/submit",
                    method="POST",
                    data={
                        "quiz_id": quiz["quiz_id"],
                        "answers": st.session_state.quiz_answers
                    }
                )
            
            if response:
                st.success(f"Quiz Submitted! Score: {response['score']:.1f}%")
                
                # Show results
                st.subheader("Results")
                results = response.get("results", {})
                
                for idx, result_data in results.items():
                    with st.expander(f"Question {int(idx) + 1}"):
                        st.markdown(f"**Question:** {result_data['question']}")
                        st.markdown(f"**Your Answer:** {result_data['user_answer']}")
                        st.markdown(f"**Correct Answer:** {result_data['correct_answer']}")
                        
                        if result_data["correct"]:
                            st.success("✅ Correct!")
                        else:
                            st.error("❌ Incorrect")
                
                # Clear current quiz
                st.session_state.current_quiz = None
                st.session_state.quiz_answers = {}


def show_progress_page():
    st.header("📈 Learning Progress")
    st.markdown("Track your learning progress and identify weak areas")
    
    # Get progress data
    with st.spinner("Loading progress..."):
        progress = make_api_request("/api/progress")
    
    if progress:
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Quizzes", progress.get("total_quizzes", 0))
        
        with col2:
            st.metric("Questions Attempted", progress.get("total_questions_attempted", 0))
        
        with col3:
            avg_score = progress.get("average_score", 0)
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        with col4:
            weak_areas_count = len(progress.get("weak_areas", []))
            st.metric("Weak Areas", weak_areas_count)
        
        st.divider()
        
        # Weak areas
        st.subheader("🎯 Weak Areas")
        weak_areas = progress.get("weak_areas", [])
        
        if weak_areas:
            for area in weak_areas:
                with st.expander(f"{area['topic']} - {area['accuracy']:.1f}% accuracy"):
                    st.progress(area['accuracy'] / 100)
                    st.text(f"Total Questions: {area['total_questions']}")
                    st.text(f"Correct Answers: {area['correct_answers']}")
        else:
            st.info("No weak areas identified. Keep up the great work! 🎉")
        
        st.divider()
        
        # Recent activity
        st.subheader("📊 Recent Activity")
        recent_activity = progress.get("recent_activity", [])
        
        if recent_activity:
            for activity in reversed(recent_activity[-10:]):
                st.text(f"Quiz: {activity.get('quiz_id', '')[:8]}... | "
                       f"Score: {activity.get('score', 0):.1f}% | "
                       f"Questions: {activity.get('total_questions', 0)}")
        else:
            st.info("No recent activity. Start taking quizzes to track your progress!")
    else:
        st.error("Failed to load progress data")


if __name__ == "__main__":
    main()


