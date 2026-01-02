from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.database import engine , Base
from app.core.logger  import   setup_logger

logger = setup_logger(__name__)

logger.info("Starting Simple Drive API application")

app = FastAPI(
    title="Simple Drive API",
    description="A simple object storage system with multiple backends",
    version="1.0.0",
)

@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Configure CORS
logger.debug("Configuring CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
logger.debug("Including API router with prefix /api")
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    logger.debug("Root endpoint accessed")
    return {"message": "Simple Drive API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    logger.debug("Root endpoint accessed")
    return {"status": "healthy"}