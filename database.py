from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "adaptive_diagnostic"
USE_MOCK = os.getenv("USE_MOCK_DB", "true").lower() == "true"

client = None
db = None

def connect_db():
    """Establish MongoDB connection (real or mock)."""
    global client, db

    if USE_MOCK:
        import mongomock
        client = mongomock.MongoClient()
        db = client[DATABASE_NAME]
        print("[OK] Using in-memory mock MongoDB (no external DB required)")
        return True

    try:
        client = MongoClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command("ping")
        db = client[DATABASE_NAME]
        print("[OK] Connected to MongoDB successfully")
        return True
    except Exception as e:
        print(f"[WARN] MongoDB connection failed: {e}")
        return False

def close_db():
    """Close MongoDB connection."""
    global client
    if client and not USE_MOCK:
        client.close()
        print("[INFO] MongoDB connection closed")

def get_database():
    """Returns the database instance."""
    if db is None:
        raise Exception("Database not connected.")
    return db
