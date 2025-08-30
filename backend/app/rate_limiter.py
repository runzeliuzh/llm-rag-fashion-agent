# Rate Limiting System for Anonymous Users
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, Request
import hashlib

class AnonymousRateLimiter:
    """Rate limiter for anonymous users - 20 queries per 5 hours"""
    
    def __init__(self):
        self.rate_limit_file = "data/rate_limits.json"
        self.max_queries = 20
        self.time_window_hours = 5
        self.cleanup_interval = 24 * 60 * 60  # Clean up old entries daily
        self.last_cleanup = time.time()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.rate_limit_file), exist_ok=True)
        
        # Load existing rate limits
        self.rate_limits = self._load_rate_limits()
    
    def _load_rate_limits(self) -> Dict:
        """Load rate limits from file"""
        try:
            if os.path.exists(self.rate_limit_file):
                with open(self.rate_limit_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load rate limits: {e}")
        return {}
    
    def _save_rate_limits(self):
        """Save rate limits to file"""
        try:
            with open(self.rate_limit_file, 'w') as f:
                json.dump(self.rate_limits, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save rate limits: {e}")
    
    def _get_client_id(self, request: Request) -> str:
        """Generate unique client ID from IP and User-Agent"""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Create hash of IP + User-Agent for privacy
        client_string = f"{client_ip}:{user_agent}"
        return hashlib.sha256(client_string.encode()).hexdigest()[:16]
    
    def _cleanup_old_entries(self):
        """Remove old rate limit entries"""
        if time.time() - self.last_cleanup < self.cleanup_interval:
            return
        
        current_time = time.time()
        cutoff_time = current_time - (self.time_window_hours * 3600 * 2)  # Keep 2x window
        
        # Remove old entries
        to_remove = []
        for client_id, data in self.rate_limits.items():
            if data.get('last_reset', 0) < cutoff_time:
                to_remove.append(client_id)
        
        for client_id in to_remove:
            del self.rate_limits[client_id]
        
        self.last_cleanup = current_time
        self._save_rate_limits()
    
    def check_rate_limit(self, request: Request) -> Dict:
        """
        Check if request should be rate limited
        Returns: {"allowed": bool, "remaining": int, "reset_time": str, "message": str}
        """
        self._cleanup_old_entries()
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Get or create client data
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {
                "query_count": 0,
                "first_query": current_time,
                "last_reset": current_time,
                "last_query": current_time
            }
        
        client_data = self.rate_limits[client_id]
        
        # Check if time window has passed (5 hours)
        time_since_first = current_time - client_data["first_query"]
        if time_since_first >= (self.time_window_hours * 3600):
            # Reset the window
            client_data["query_count"] = 0
            client_data["first_query"] = current_time
            client_data["last_reset"] = current_time
        
        # Check if rate limit exceeded
        if client_data["query_count"] >= self.max_queries:
            time_until_reset = (self.time_window_hours * 3600) - time_since_first
            reset_time = datetime.fromtimestamp(current_time + time_until_reset)
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": reset_time.strftime("%H:%M:%S UTC"),
                "message": f"Rate limit exceeded. You can make {self.max_queries} queries every {self.time_window_hours} hours. Try again at {reset_time.strftime('%H:%M:%S UTC')}."
            }
        
        # Allow the request and increment counter
        client_data["query_count"] += 1
        client_data["last_query"] = current_time
        remaining = self.max_queries - client_data["query_count"]
        
        # Calculate reset time
        reset_timestamp = client_data["first_query"] + (self.time_window_hours * 3600)
        reset_time = datetime.fromtimestamp(reset_timestamp)
        
        self._save_rate_limits()
        
        return {
            "allowed": True,
            "remaining": remaining,
            "reset_time": reset_time.strftime("%H:%M:%S UTC"),
            "message": f"Query allowed. {remaining} queries remaining until {reset_time.strftime('%H:%M:%S UTC')}."
        }

# Global rate limiter instance
rate_limiter = AnonymousRateLimiter()

async def check_rate_limit_middleware(request: Request):
    """Middleware function to check rate limits"""
    result = rate_limiter.check_rate_limit(request)
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": result["message"],
                "remaining": result["remaining"],
                "reset_time": result["reset_time"]
            }
        )
    
    return result
