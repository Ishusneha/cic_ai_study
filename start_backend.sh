#!/bin/bash
echo "Starting AI Study Assistant Backend..."
cd backend
uvicorn app.main:app --reload --port 8000


