import secrets
from fastapi import Request, HTTPException
from app.config import settings

def require_demo_access(request: Request) -> None:
    if not settings.demo_access_required:
        return

    code = request.headers.get("x-demo-access-code")
    
    if not code:
        raise HTTPException(status_code=401, detail="Demo access code required")
        
    expected_code = settings.demo_access_code
    
    if not expected_code:
        # If required but not configured, fail closed
        raise HTTPException(status_code=401, detail="Demo access code required")
        
    if not secrets.compare_digest(code, expected_code):
        raise HTTPException(status_code=401, detail="Demo access code required")
