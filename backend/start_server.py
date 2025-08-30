#!/usr/bin/env python3
"""
Start the fashion RAG server with DeepSeek API integration
Usage: 
1. Copy .env.example to .env and add your API key
2. Run: python start_server.py
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        print(f"✅ DeepSeek API Key found: {api_key[:8]}...")
    else:
        print("⚠️  No DEEPSEEK_API_KEY found - will use fallback methods")
        print("   Copy .env.example to .env and add your API key")
    
    # Add current directory to path
    sys.path.append('.')
    
    # Import and start the app
    from app.main import app
    
    print("🚀 Starting Fashion RAG API server with DeepSeek integration...")
    
    # Get port from environment (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"📡 API will be available at: http://{host}:{port}")
    print("📝 Test endpoint: POST /api/v1/query")
    print("   Body: {\"query\": \"What are autumn fashion trends?\"}")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
