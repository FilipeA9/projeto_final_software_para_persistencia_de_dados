"""
Rate Limiting Middleware - Protect API endpoints from abuse.

Simple in-memory rate limiting based on IP address.
"""

from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio


class RateLimiter:
    """Simple rate limiter using sliding window."""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute per IP
        """
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.cleanup_interval = 60  # Cleanup every 60 seconds
        self.last_cleanup = datetime.now()
    
    def cleanup_old_requests(self):
        """Remove requests older than 1 minute."""
        now = datetime.now()
        if (now - self.last_cleanup).seconds >= self.cleanup_interval:
            cutoff = now - timedelta(minutes=1)
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    req_time for req_time in self.requests[ip]
                    if req_time > cutoff
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
            self.last_cleanup = now
    
    async def check_rate_limit(self, request: Request):
        """
        Check if request exceeds rate limit.
        
        Args:
            request: FastAPI request
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Cleanup old requests periodically
        self.cleanup_old_requests()
        
        # Check rate limit
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Get recent requests from this IP
        recent_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
        
        if len(recent_requests) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
            )
        
        # Add current request
        self.requests[client_ip].append(now)


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=120)


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to apply rate limiting to all requests.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/route handler
        
    Returns:
        Response from next handler
    """
    # Skip rate limiting for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    # Check rate limit
    await rate_limiter.check_rate_limit(request)
    
    # Continue with request
    response = await call_next(request)
    return response
