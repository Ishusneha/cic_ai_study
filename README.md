# AI Study Assistant for Exam Preparation

An AI-powered study assistant that helps students understand, practice, and revise syllabus content by conversing in natural language with their own study materials using a Retrieval-Augmented Generation (RAG) pipeline.

## Features

- 📚 **Document Upload**: Upload syllabus documents, class notes, PDFs, and textbooks
- 💬 **Natural Language Q&A**: Ask questions about topics, chapters, or the full syllabus
- 📝 **Quiz Generation**: Generate MCQs and short answer questions from uploaded content
- 📊 **Progress Tracking**: Track learning progress, attempted questions, accuracy, and weak areas
- 🔍 **Grounded Answers**: Answers are generated only from uploaded content to minimize hallucinations

## Technology Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **RAG Pipeline**: LangChain
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence-Transformers
- **LLM**: OpenAI (configurable to use Llama-3/Mistral)

## Project Structure

```
cic/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py         # Pydantic models
│   │   ├── rag_pipeline.py  # RAG pipeline implementation
│   │   ├── quiz_generator.py # Quiz generation logic
│   │   └── progress_tracker.py # Progress tracking
│   └── uploads/             # Uploaded documents storage
├── frontend/
│   └── app.py               # Streamlit application
├── vector_store/            # ChromaDB vector store
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
VECTOR_STORE_PATH=./vector_store
UPLOAD_DIR=./backend/uploads
```

### 3. Run the Backend

**Windows:**
```bash
start_backend.bat
```

**Linux/Mac:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Or manually:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Run the Frontend

**Windows:**
```bash
start_frontend.bat
```

**Linux/Mac:**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

**Or manually:**
```bash
streamlit run frontend/app.py
```

The frontend will be available at `http://localhost:8501`

> **Note**: Make sure the backend is running before starting the frontend!

## API Endpoints

### Document Upload
- `POST /api/upload` - Upload a document (PDF, DOCX, TXT)

### Chat
- `POST /api/chat` - Ask questions about uploaded content
- `GET /api/chat/history` - Get chat history

### Quiz
- `POST /api/quiz/generate` - Generate quiz questions
- `POST /api/quiz/submit` - Submit quiz answers
- `GET /api/quiz/history` - Get quiz history

### Progress
- `GET /api/progress` - Get learning progress and analytics
- `GET /api/progress/weak-areas` - Get identified weak areas

## Usage

1. **Upload Documents**: Use the frontend to upload your study materials (PDFs, DOCX, TXT)

2. **Ask Questions**: Chat with the AI assistant about topics in your uploaded content

3. **Generate Quizzes**: Create practice questions from your study materials

4. **Track Progress**: View your quiz performance and identify weak areas

## Demo

### Document Upload
Upload your syllabus documents, notes, or textbooks through the web interface.

### Chat Interface
Ask questions like:
- "Explain the concept of photosynthesis"
- "What are the key points in chapter 3?"
- "Summarize the main topics covered"

### Quiz Generation
Generate quizzes with:
- Multiple choice questions
- Short answer questions
- Questions based on specific topics or chapters

### Progress Analytics
View:
- Total questions attempted
- Accuracy percentage
- Weak areas identified
- Learning progress over time

## Configuration

The system supports multiple LLM providers. To use a different model:

1. Update the `.env` file with your API key
2. Modify `backend/app/rag_pipeline.py` to use the desired LLM provider
3. Supported providers: OpenAI, Llama-3 (via Ollama), Mistral

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

