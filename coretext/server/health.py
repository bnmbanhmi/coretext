from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict

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
    
    Verifies that the request originates from localhost (127.0.0.1 or ::1).
    
    Returns:
        Dict[str, str]: {"status": "OK"}
        
    Raises:
        HTTPException: 403 Forbidden if request is not from localhost.
    """
    return {"status": "OK"}
