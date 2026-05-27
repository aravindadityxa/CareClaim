from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings
from typing import AsyncGenerator

# --- SQL Database (SQLite or PostgreSQL) ---
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "dev",
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
AsyncSessionFactory = async_sessionmaker(
    async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get an async database session.
    """
    async with AsyncSessionFactory() as session:
        yield session

async def connect_db():
    """Connect to the database (SQLite or PostgreSQL)."""
    try:
        async with async_engine.connect() as conn:
            if "sqlite" in settings.DATABASE_URL:
                print("✓ SQLite connection successful.")
            else:
                print("✓ PostgreSQL connection successful.")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")


async def disconnect_db():
    """Disconnect from the database."""
    await async_engine.dispose()
    db_type = "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL"
    print(f"✓ {db_type} connection closed.")


# --- MongoDB (Motor) - Optional ---
mongo_client: AsyncIOMotorClient | None = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Get the MongoDB client."""
    if mongo_client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect_mongo() first.")
    return mongo_client

async def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Dependency function to get the MongoDB database instance.
    """
    if not settings.MONGO_ENABLED:
        return None
    
    client = get_mongo_client()
    db_name = settings.MONGO_URI.split("/")[-1].split("?")[0]
    return client[db_name]

async def connect_mongo():
    """Connect to the MongoDB database (optional)."""
    global mongo_client
    
    if not settings.MONGO_ENABLED:
        print("MongoDB is disabled in configuration.")
        return False
    
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
        await mongo_client.admin.command('ping')
        print("✓ MongoDB connection successful.")
        return True
    except Exception as e:
        print(f"⚠ MongoDB connection failed (this is OK for local dev): {e}")
        return False


async def disconnect_mongo():
    """Disconnect from the MongoDB database."""
    if mongo_client:
        mongo_client.close()
        print("✓ MongoDB connection closed.")
