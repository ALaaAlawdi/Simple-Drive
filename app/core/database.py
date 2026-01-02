from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings


# Database URL
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRESQL_DB_USER}:{settings.POSTGRESQL_DB_PASSWORD}"
    f"@{settings.POSTGRESQL_DB_HOST}:{settings.POSTGRESQL_DB_PORT}/{settings.POSTGRESQL_DB_NAME}"
)

# create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
# create session factory
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as db:
        yield db