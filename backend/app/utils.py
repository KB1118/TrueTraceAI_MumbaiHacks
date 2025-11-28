"""
Utility functions for security, pagination, and helpers.
"""
from typing import List, Tuple
from sqlalchemy.orm import Query
from fastapi import Request


def paginate_query(query: Query, page: int = 1, page_size: int = 20) -> Tuple[List, int, int]:
    """
    Paginate a SQLAlchemy query.
    Returns: (items, total_count, total_pages)
    """
    total_count = query.count()
    total_pages = (total_count + page_size - 1) // page_size
    
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return items, total_count, total_pages


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    if request.client:
        return request.client.host
    return "unknown"


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize and truncate text input."""
    if not text:
        return ""
    # Remove potentially harmful characters and truncate
    sanitized = text.strip()[:max_length]
    return sanitized

