"""
Setup script for AI Study Assistant
"""
import os
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "backend/uploads",
        "backend/progress_data",
        "vector_store"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
VECTOR_STORE_PATH=./vector_store
UPLOAD_DIR=./backend/uploads
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✓ Created .env file - Please update OPENAI_API_KEY")
    else:
        print("✓ .env file already exists")

if __name__ == "__main__":
    print("Setting up AI Study Assistant...")
    create_directories()
    create_env_file()
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your OPENAI_API_KEY")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run backend: cd backend && uvicorn app.main:app --reload")
    print("4. Run frontend: streamlit run frontend/app.py")


