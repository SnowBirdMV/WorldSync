"""
app/routes/auth.py

Holds API key authentication decorator and any other auth-related utilities.
"""

from functools import wraps
from flask import request, abort, current_app
from app.config import API_KEY


def require_api_key(f):
    """
    Decorator to require an API key for certain routes.
    Checks 'x-api-key' in request headers.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key != API_KEY:
            current_app.logger.warning(f"Unauthorized access attempt with API key: {key}")
            abort(403, description="Forbidden: Invalid or missing API key.")
        return f(*args, **kwargs)
    return decorated
