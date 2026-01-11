# AI Study Assistant for Exam Preparation

An AI-powered study assistant that helps students understand, practice, and revise syllabus content by conversing in natural language with their own study materials using a Retrieval-Augmented Generation (RAG) pipeline.

## Features

- 📚 **Document Upload**: Upload syllabus documents, class notes, PDFs, and textbooks
- 💬 **Natural Language Q&A**: Ask questions about topics, chapters, or the full syllabus
- 📝 **Quiz Generation**: Generate MCQs and short answer questions from uploaded content
- 📊 **Progress Tracking**: Track learning progress, attempted questions, accuracy, and weak areas
- 🔍 **Grounded Answers**: Answers are generated only from uploaded content to minimize hallucinations

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React (Vite)
- **RAG Pipeline**: LangChain
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **LLM**: Ollama (llama3.2:latest)
- **Deployment**: Docker & Docker Compose support

## Project Structure

```
ai_study/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py         # Pydantic models
│   │   ├── rag_pipeline.py  # RAG pipeline implementation
│   │   ├── quiz_generator.py # Quiz generation logic
│   │   └── progress_tracker.py # Progress tracking
│   ├── uploads/             # Uploaded documents storage
│   ├── progress_data/       # Quiz results and progress data
│   └── vector_store/        # ChromaDB vector store
├── frontend/
│   ├── src/                 # React frontend
│   │   ├── components/      # React components (Chat, Quiz, Progress, DocumentUpload)
│   │   ├── services/        # API service layer
│   │   ├── App.jsx          # Main React app
│   │   └── main.jsx         # React entry point
│   ├── package.json         # Node.js dependencies
│   ├── vite.config.js       # Vite configuration
│   └── index.html           # HTML template
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Backend Dockerfile
├── env.example             # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Setup Ollama

First, install Ollama from https://ollama.ai, then pull the required model:

```bash
ollama pull llama3.2:latest
```

Make sure Ollama is running (it should start automatically on installation).

### 3. Environment Configuration

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` file with your configuration:

```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434
VECTOR_STORE_PATH=./backend/vector_store
UPLOAD_DIR=./backend/uploads
```

### 4. Run the Backend

**Option 1: Using Docker (Recommended)**

```bash
docker compose up -d --build backend
```

The API will be available at `http://localhost:8000`

**Option 2: Manual Setup**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Run the Frontend

**React Frontend:**

```bash
cd frontend
npm install
npm run dev
```

The React frontend will be available at `http://localhost:5173`

> **Note**: Make sure the backend is running before starting the frontend!

### 6. Using Docker Compose (Full Stack)

To run both backend and frontend with Docker:

```bash
docker compose up -d --build
```

This will start both services. The backend will be at `http://localhost:8000` and frontend at the configured port.

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

The system uses Ollama for LLM and local embeddings. To configure:

1. Install Ollama from https://ollama.ai
2. Pull the required model: `ollama pull llama3.2:latest`
3. Ensure Ollama is running (default: http://localhost:11434)
4. The default model is `llama3.2:latest` which can be changed in the `.env` file
5. You can change the Ollama base URL if running on a different host/port

### Docker Configuration

When using Docker, the backend uses `network_mode: host` to access Ollama running on your host machine. Make sure Ollama is running on your host before starting the Docker container.

### Storage Locations

- **Uploaded Documents**: `backend/uploads/`
- **Quiz Data**: `backend/progress_data/quizzes.json`
- **Progress Statistics**: `backend/progress_data/progress.json`
- **Vector Store**: `backend/vector_store/` (ChromaDB database)

## Troubleshooting

### Backend won't start
- Make sure port 8000 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Ollama is running: `ollama list`
- Check that the model is pulled: `ollama list` should show `llama3.2:latest`

### Frontend can't connect to backend
- Ensure the backend is running on port 8000
- Check the API_BASE_URL in `frontend/src/services/api.js` matches your backend URL
- If using Docker, ensure network configuration is correct

### Document upload fails
- Check file format (PDF, DOCX, TXT only)
- Ensure file is not corrupted
- Check backend logs for error messages
- Verify `backend/uploads/` directory exists and is writable

### Quiz generation fails
- Make sure you have uploaded at least one document
- Verify Ollama is running and the model is available
- Try with fewer questions first
- Check Ollama logs if the model fails to respond

### Docker issues
- If Ollama connection fails in Docker, ensure Ollama is running on the host
- For Linux, Docker uses `network_mode: host` to access host services
- Check Docker logs: `docker logs ai-study-backend`

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

