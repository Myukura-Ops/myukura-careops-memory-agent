import secrets
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.config import settings

logger = logging.getLogger(__name__)


def require_demo_access(request: Request) -> None:
    """Enforce demo access code on protected endpoints.

    Uses constant-time comparison to prevent timing attacks.
    Fails closed: if the code is required but not configured on the
    server, all requests are rejected.
    """
    if not settings.demo_access_required:
        return

    code = request.headers.get("x-demo-access-code")

    if not code:
        raise HTTPException(
            status_code=401,
            detail={
                "error_type": "AUTH_REQUIRED",
                "message": "Demo access code is required.",
                "suggestion": "Include the x-demo-access-code header.",
                "retryable": False,
                "status": "failed",
            },
        )

    expected_code = settings.demo_access_code

    if not expected_code:
        logger.warning("Demo access required but DEMO_ACCESS_CODE is not configured on the server.")
        raise HTTPException(
            status_code=503,
            detail={
                "error_type": "AUTH_NOT_CONFIGURED",
                "message": "Demo access is required but not yet configured.",
                "suggestion": "Contact the administrator.",
                "retryable": True,
                "status": "failed",
            },
        )

    if not secrets.compare_digest(code, expected_code):
        raise HTTPException(
            status_code=403,
            detail={
                "error_type": "AUTH_INVALID",
                "message": "Invalid demo access code.",
                "suggestion": "Check the access code and try again.",
                "retryable": False,
                "status": "failed",
            },
        )
