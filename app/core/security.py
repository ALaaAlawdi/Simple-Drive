from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings
from .logger import setup_logger

logger = setup_logger(__name__)
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Simple token verification.
    """

    logger.debug("Verifying authentication token")
    if credentials.scheme != "Bearer":
        logger.warning("Invalid authentication scheme")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme"
        )
    
    if credentials.credentials != settings.AUTH_TOKEN:
        logger.warning("Invalid authentication token")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    logger.debug("Authentication successful")
    return {"authenticated": True}