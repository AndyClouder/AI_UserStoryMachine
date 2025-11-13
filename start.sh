#!/bin/bash
# Render平台启动脚本

echo "Starting AI User Story Machine..."
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting FastAPI application..."
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}