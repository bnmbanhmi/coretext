from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict
from importlib.metadata import version

router = APIRouter()

async def verify_localhost(request: Request):
    """
    Dependency to ensure request is from localhost.
    """
    client_host = request.client.host if request.client else None
    allowed_hosts = ["127.0.0.1", "::1"]
    
    if client_host not in allowed_hosts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Localhost only."
        )

@router.get("/health", dependencies=[Depends(verify_localhost)])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify service status.
    Returns version from package metadata.
    """
    try:
        pkg_version = version("coretext")
    except Exception:
        pkg_version = "unknown"
        
    return {"status": "OK", "version": pkg_version}
