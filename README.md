# 🎨 Fashion Assistant

A fashion chatbot demonstrating **Retrieval-Augmented Generation (RAG)** with FastAPI backend and React frontend.

![Fashion](https://img.shields.io/badge/Fashion-Assistant-pink) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green) ![React](https://img.shields.io/badge/React-18.2.0-blue) ![Python](https://img.shields.io/badge/Python-3.9+-yellow)

**Tech Stack**: FastAPI + React + ChromaDB + DeepSeek LLM  
**Features**: RAG implementation, rate limiting, web interface

## 🏗️ Architecture

```
React Frontend ── FastAPI Backend ── DeepSeek LLM
     │                 │
Rate Limiting    ChromaDB Vector DB
```

**Flow**: User query → Vector search → Context augmentation → LLM generation → Response

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/runzeliuzh/ai-fashion-assistant.git
cd ai-fashion-assistant

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python start_server.py  # → localhost:8000

# Frontend (new terminal)
cd frontend
npm install && npm start  # → localhost:3000
```

## ✨ Features

- **Fashion Chat**: Basic conversation about fashion topics
- **Rate Limiting**: 20 queries per 5 hours 
- **Status Display**: Shows connection status
- **Web Interface**: Simple React frontend

## 📁 Structure

```
backend/app/main.py           # API endpoints
backend/app/rag_chain.py      # Vector search integration
frontend/src/components/      # React components
backend/data/chroma_db/       # Vector database
```

## 🌐 Deployment

- **Frontend**: Vercel 
- **Backend**: Railway 


## 📄 License

This project is licensed under a **Custom Source-Available License**.

**✅ What you CAN do:**
- View and study the source code
- Use for educational purposes
- Fork for learning and experimentation
- Reference in academic work or portfolios

**❌ What you CANNOT do:**
- Use for commercial purposes
- Distribute or sell the application
- Create commercial derivatives
- Use in production without permission

**💼 Commercial Use:** Contact the author for licensing options.

For full license details, see the [LICENSE](LICENSE) file.

---

*Portfolio project demonstrating basic RAG implementation*