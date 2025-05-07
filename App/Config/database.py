# App/Config/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os


# 🌱 Load environment variables
load_dotenv()

# Base class for all models
Base = declarative_base()

# 🌐 Load DB URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set in the environment variables!")

# Create Async Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create Session Local
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session


# create the table in PostgreSQL.
async def init_db():
    from App.Models import stock  # Import models inside the function
    print("Initializing Database...")  # Debugging message
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database Initialized!")  # Debugging message

