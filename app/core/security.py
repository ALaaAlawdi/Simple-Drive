from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Simple token verification.
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme"
        )
    
    if credentials.credentials != settings.AUTH_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    return {"authenticated": True}