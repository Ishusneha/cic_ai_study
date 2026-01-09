# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one from https://platform.openai.com/api-keys)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
VECTOR_STORE_PATH=./vector_store
UPLOAD_DIR=./backend/uploads
```

Or run the setup script:

```bash
python setup.py
```

Then edit `.env` and add your OpenAI API key.

### 3. Start the Backend

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

### 4. Start the Frontend

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

The frontend will open automatically in your browser at `http://localhost:8501`

## Usage

1. **Upload Documents**: Use the sidebar to upload PDF, DOCX, or TXT files
2. **Chat**: Ask questions about your uploaded content
3. **Generate Quizzes**: Create practice questions from your materials
4. **Track Progress**: View your performance and weak areas

## Troubleshooting

### Backend won't start
- Make sure port 8000 is not in use
- Check that all dependencies are installed
- Verify your `.env` file has the correct OpenAI API key

### Frontend can't connect to backend
- Ensure the backend is running on port 8000
- Check the API_BASE_URL in `frontend/app.py` matches your backend URL

### Document upload fails
- Check file format (PDF, DOCX, TXT only)
- Ensure file is not corrupted
- Check backend logs for error messages

### Quiz generation fails
- Make sure you have uploaded at least one document
- Check your OpenAI API key is valid and has credits
- Try with fewer questions first

## API Documentation

Once the backend is running, visit:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc


