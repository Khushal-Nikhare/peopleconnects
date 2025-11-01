"""
Create test data for PeopleConnects
Adds multiple users and posts with photos, likes, comments, followers
"""
import asyncio
from datetime import datetime, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'backend'))
from auth import hash_password

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "peopleconnects"

# Test data
TEST_USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "password123"},
    {"username": "bob", "email": "bob@example.com", "password": "password123"},
    {"username": "charlie", "email": "charlie@example.com", "password": "password123"},
    {"username": "diana", "email": "diana@example.com", "password": "password123"},
    {"username": "eve", "email": "eve@example.com", "password": "password123"},
]

TEST_POSTS_CONTENT = [
    "Just had an amazing cup of coffee! ☕",
    "Beautiful sunset today 🌅",
    "Working on a new project, super excited!",
    "Anyone else love coding at night? 💻",
    "Finally finished that book I've been reading 📚",
    "Weekend vibes! Time to relax 😎",
    "Just launched my new website! Check it out!",
    "Learning something new every day 🚀",
    "Great day at the park with friends 🌳",
    "Dinner was delicious tonight! 🍝",
    "Traveling to new places is the best",
    "Productive day at work today",
    "Can't wait for the weekend!",
    "Just watched an incredible movie 🎬",
    "Morning run completed! Feeling energized 🏃",
    "Pizza night! Who's in? 🍕",
    "Building something cool with Python",
    "Music makes everything better 🎵",
    "Grateful for all the little things",
    "New beginnings are always exciting!",
]

async def create_test_data():
    """Create test users and posts with relationships"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🗑️  Clearing existing data...")
    await db.users.delete_many({})
    await db.posts.delete_many({})
    
    print("👥 Creating test users...")
    user_ids = []
    
    for user_data in TEST_USERS:
        user = {
            "username": user_data["username"],
            "email": user_data["email"],
            "password": hash_password(user_data["password"]),
            "profile_pic": None,
            "followers": [],
            "following": [],
            "created_at": datetime.utcnow()
        }
        result = await db.users.insert_one(user)
        user_ids.append(user_data["username"])
        print(f"   ✅ Created user: {user_data['username']}")
    
    # Create follower relationships
    print("\n🤝 Creating follower relationships...")
    for i, username in enumerate(user_ids):
        # Each user follows 2-3 random other users
        num_following = random.randint(2, 3)
        possible_follows = [u for u in user_ids if u != username]
        to_follow = random.sample(possible_follows, num_following)
        
        for follow_user in to_follow:
            # Add to following list
            await db.users.update_one(
                {"username": username},
                {"$addToSet": {"following": follow_user}}
            )
            # Add to followers list
            await db.users.update_one(
                {"username": follow_user},
                {"$addToSet": {"followers": username}}
            )
        
        print(f"   ✅ {username} now follows {len(to_follow)} users")
    
    # Create posts
    print("\n📝 Creating test posts...")
    post_ids = []
    
    for i, content in enumerate(TEST_POSTS_CONTENT):
        # Random author
        author = random.choice(user_ids)
        
        # Random timestamp (last 7 days)
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
        
        post = {
            "author": author,
            "content": content,
            "image": None,  # No images for test data (can be added manually)
            "timestamp": timestamp,
            "likes": [],
            "comments": []
        }
        
        # Add random likes (0-4 users)
        num_likes = random.randint(0, 4)
        possible_likers = [u for u in user_ids if u != author]
        if possible_likers and num_likes > 0:
            likers = random.sample(possible_likers, min(num_likes, len(possible_likers)))
            post["likes"] = likers
        
        # Add random comments (0-3 comments)
        num_comments = random.randint(0, 3)
        if num_comments > 0:
            possible_commenters = [u for u in user_ids if u != author]
            if possible_commenters:
                comment_texts = [
                    "Love this!",
                    "Great post!",
                    "Thanks for sharing!",
                    "This is awesome!",
                    "Totally agree!",
                    "Nice one!",
                    "So cool!",
                    "Amazing!",
                ]
                
                for _ in range(num_comments):
                    commenter = random.choice(possible_commenters)
                    comment_text = random.choice(comment_texts)
                    comment = {
                        "username": commenter,
                        "text": comment_text,
                        "timestamp": timestamp + timedelta(hours=random.randint(1, 12))
                    }
                    post["comments"].append(comment)
        
        result = await db.posts.insert_one(post)
        post_ids.append(result.inserted_id)
        print(f"   ✅ Created post by {author} ({len(post['likes'])} likes, {len(post['comments'])} comments)")
    
    # Display summary
    print("\n" + "="*60)
    print("✅ TEST DATA CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"Total Users: {len(user_ids)}")
    print(f"Total Posts: {len(post_ids)}")
    print("\nTest User Credentials:")
    print("-" * 40)
    for user in TEST_USERS:
        print(f"  Username: {user['username']}")
        print(f"  Password: {user['password']}")
        print()
    
    # Show some stats
    total_likes = 0
    total_comments = 0
    for post_id in post_ids:
        post = await db.posts.find_one({"_id": post_id})
        total_likes += len(post.get("likes", []))
        total_comments += len(post.get("comments", []))
    
    print(f"Total Likes: {total_likes}")
    print(f"Total Comments: {total_comments}")
    print("="*60)
    
    # Show follower stats
    print("\nFollower Statistics:")
    print("-" * 40)
    for username in user_ids:
        user = await db.users.find_one({"username": username})
        followers_count = len(user.get("followers", []))
        following_count = len(user.get("following", []))
        print(f"  {username}: {followers_count} followers, {following_count} following")
    
    print("\n🎉 Ready to start the application!")
    print("Run: python -m backend.main")
    
    client.close()

if __name__ == "__main__":
    print("="*60)
    print("  PEOPLECONNECTS TEST DATA CREATOR")
    print("="*60)
    print("\n⚠️  This will DELETE all existing data!")
    print("Make sure MongoDB is running on localhost:27017\n")
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() in ["yes", "y"]:
        asyncio.run(create_test_data())
    else:
        print("❌ Cancelled")
