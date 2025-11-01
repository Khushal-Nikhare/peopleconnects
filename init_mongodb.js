// MongoDB Initialization Script for PeopleConnects
// Run this script with: mongosh < init_mongodb.js

// Switch to peopleconnects database
use peopleconnects;

// Drop existing collections (optional - for fresh start)
// db.users.drop();
// db.posts.drop();

// Create collections
db.createCollection("users");
db.createCollection("posts");

// Create indexes for optimization
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.posts.createIndex({ "timestamp": -1 });
db.posts.createIndex({ "author": 1 });

// Verify indexes
print("=== Users Collection Indexes ===");
printjson(db.users.getIndexes());

print("\n=== Posts Collection Indexes ===");
printjson(db.posts.getIndexes());

// Show statistics
print("\n=== Database Statistics ===");
print("Users count: " + db.users.countDocuments());
print("Posts count: " + db.posts.countDocuments());

print("\n✅ MongoDB initialization complete!");
print("Database: peopleconnects");
print("Collections: users, posts");
print("Indexes: Created successfully");
