from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

# Async Session
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

# Declarative Base for ORM models
Base = declarative_base()

# Dependency for FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session
