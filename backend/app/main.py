# Fashion RAG API - AI-Powered Fashion Assistant
import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.rag_chain import get_rag_response
from app.rate_limiter import check_rate_limit_middleware

app = FastAPI(
    title="Fashion RAG API",
    description="AI-Powered Fashion Assistant with Real-time Trend Analysis",
    version="1.0.0"
)

# Security middleware - Check Origin header
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Allow all methods for localhost development
    if request.client.host in ["127.0.0.1", "localhost"]:
        response = await call_next(request)
        return response
    
    # Allow healthcheck endpoints without origin validation
    if request.url.path in ["/", "/health", "/healthz"]:
        response = await call_next(request)
        return response
    
    # For production API endpoints, check Origin and Referer headers
    origin = request.headers.get("origin")
    referer = request.headers.get("referer", "")
    
    # Get allowed domains from environment
    frontend_urls = os.getenv("FRONTEND_URLS", "http://localhost:3000")
    allowed_domains = [url.strip() for url in frontend_urls.split(",")]
    
    # Check if request is from allowed domain
    if not any(domain in str(origin) or domain in referer for domain in allowed_domains):
        raise HTTPException(status_code=403, detail="Access denied: Invalid origin")
    
    response = await call_next(request)
    return response

# CORS configuration - SECURE: Use environment variables
FRONTEND_URLS = os.getenv("FRONTEND_URLS", "http://localhost:3000,http://localhost:3001,http://localhost:3002")
ALLOWED_ORIGINS = [url.strip() for url in FRONTEND_URLS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Configured via environment variables
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "message": "Fashion RAG API is running", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "message": "Fashion RAG API is operational"
    }

@app.get("/api/v1/rate-limit-status")
async def get_rate_limit_status(request: Request):
    """Check current rate limit status for the client"""
    from app.rate_limiter import rate_limiter
    
    client_id = rate_limiter._get_client_id(request)
    current_time = time.time()
    
    if client_id not in rate_limiter.rate_limits:
        return {
            "queries_used": 0,
            "queries_remaining": rate_limiter.max_queries,
            "reset_time": "N/A",
            "time_window_hours": rate_limiter.time_window_hours
        }
    
    client_data = rate_limiter.rate_limits[client_id]
    time_since_first = current_time - client_data["first_query"]
    
    if time_since_first >= (rate_limiter.time_window_hours * 3600):
        # Window has expired
        queries_used = 0
        queries_remaining = rate_limiter.max_queries
        reset_time = "Window expired - resets on next query"
    else:
        queries_used = client_data["query_count"]
        queries_remaining = rate_limiter.max_queries - queries_used
        reset_timestamp = client_data["first_query"] + (rate_limiter.time_window_hours * 3600)
        reset_time = datetime.fromtimestamp(reset_timestamp).strftime("%H:%M:%S UTC")
    
    return {
        "queries_used": queries_used,
        "queries_remaining": queries_remaining,
        "reset_time": reset_time,
        "time_window_hours": rate_limiter.time_window_hours
    }

@app.post("/api/v1/query")
async def query_fashion(request: QueryRequest, http_request: Request):
    """
    Query the fashion RAG system for style advice, trends, and outfit recommendations
    Rate limited to 20 queries per 5 hours for anonymous users
    """
    try:
        # Check rate limiting for anonymous users
        rate_limit_result = await check_rate_limit_middleware(http_request)
        
        # Basic validation
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(status_code=400, detail="Query too short. Please provide at least 3 characters.")
        
        if len(request.query) > 500:
            raise HTTPException(status_code=400, detail="Query too long. Please limit to 500 characters.")
        
        # Query the RAG system
        result = await get_rag_response(request.query)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate response. Please try again.")
        
        return {
            "response": result,
            "query": request.query,
            "status": "success",
            "rate_limit": {
                "remaining": rate_limit_result["remaining"],
                "reset_time": rate_limit_result["reset_time"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Query error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
