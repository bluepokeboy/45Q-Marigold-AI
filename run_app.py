#!/usr/bin/env python3
"""
Simple launcher for the 45Q Marigold AI application
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the FastAPI app
from app.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting 45Q Marigold AI Application...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🌐 Web Interface will be available at: http://localhost:8000")
    print("💚 Health Check will be available at: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 