"""
MongoDB Database Configuration
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

MONGO_URL = "mongodb://localhost:27017"
DATABASE_NAME = "peopleconnects"

client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo():
    """Connect to MongoDB and create indexes for optimization"""
    global client
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    # Create indexes for better performance
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    await db.posts.create_index([("timestamp", -1)])  # For sorting by newest
    await db.posts.create_index("author")  # For filtering by author
    
    print("✅ Connected to MongoDB and indexes created")

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("❌ MongoDB connection closed")

def get_database():
    """Get database instance"""
    return client[DATABASE_NAME]
