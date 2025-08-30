# 🎨 Fashion RAG Assistant

AI-powered fashion advisor demonstrating **Retrieval-Augmented Generation (RAG)** with FastAPI backend and React frontend.

![Fashion AI](https://img.shields.io/badge/Fashion-AI-pink) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green) ![React](https://img.shields.io/badge/React-18.2.0-blue) ![Python](https://img.shields.io/badge/Python-3.9+-yellow)

**Tech Stack**: FastAPI + React + ChromaDB + DeepSeek LLM  
**Features**: RAG implementation, rate limiting, real-time UI, production deployment

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
git clone https://github.com/runzeliuzh/llm-rag-fashion-agent.git
cd llm-rag-fashion-agent

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

- **AI Fashion Advice**: Natural conversation with contextual responses
- **Rate Limiting**: 20 queries per 5 hours for cost control
- **Real-time Status**: Connection monitoring with offline handling
- **Production Ready**: Docker deployment, error handling, security

## 📁 Structure

```
backend/app/main.py           # API endpoints & RAG logic
backend/app/rag_chain.py      # Vector search & LLM integration
frontend/src/components/      # React UI components
backend/data/chroma_db/       # Vector database (12 articles)
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

*Portfolio project demonstrating full-stack AI application development*