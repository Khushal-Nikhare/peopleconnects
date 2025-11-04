# 🌐 PeopleConnects - Advanced Social Media Platform

A beginner-friendly, fully-featured social media web application built with **FastAPI** (Python backend), **MongoDB** (database), and **Bootstrap 5 + HTML** (frontend).

## 🎉 Version 2.0 - Complete Feature Set

### ✨ All Features Implemented

#### 🔐 Authentication & Security
- ✅ User Registration with validation
- ✅ Login with JWT tokens
- ✅ Password hashing (bcrypt)
- ✅ Secure cookie sessions
- ✅ Error messages for wrong credentials

#### 👤 User Profiles
- ✅ Profile pictures (upload & change)
- ✅ Edit profile (username, email, password)
- ✅ Unique username validation
- ✅ Follower/following counts and lists
- ✅ Profile picture display everywhere

#### 📝 Post System
- ✅ Create text posts
- ✅ Upload images with posts
- ✅ Individual post pages (`/posts/{post_id}`)
- ✅ Like/unlike toggle button
- ✅ Comment on posts
- ✅ Author profile pictures

#### 📰 Feed System
- ✅ Global feed (all posts)
- ✅ Following filter (personalized)
- ✅ Popular filter (most-liked)
- ✅ Recent filter (last 24 hours)

#### 👥 Follower System
- ✅ Follow/unfollow users
- ✅ Clickable follower lists
- ✅ Clickable following lists
- ✅ Profile pictures in lists

#### 🔍 Search Functionality
- ✅ Search users by username
- ✅ Search posts by content
- ✅ Case-insensitive search
- ✅ Results page with counts

#### 🛡️ Admin Dashboard
- ✅ Admin login (`admin` / `admin123`)
- ✅ User statistics
- ✅ Post statistics
- ✅ Most liked posts
- ✅ User management (delete)
- ✅ Post management (delete)

#### 🎨 Professional UI/UX
- ✅ Bootstrap 5 framework
- ✅ Bootstrap Icons (no emojis!)
- ✅ Responsive mobile design
- ✅ Clean color scheme
- ✅ Smooth animations
- ✅ Professional typography

#### ⚡ Performance & Optimization
- ✅ MongoDB indexes
- ✅ Query pagination
- ✅ Image optimization
- ✅ Fast database queries
- ✅ Efficient aggregations

---

## 📁 Project Structure

```
peoplesconnect_1/
├── backend/
│   ├── main.py          # FastAPI routes and application
│   ├── database.py      # MongoDB connection and indexes
│   ├── models.py        # Pydantic models for validation
│   └── auth.py          # Authentication utilities (JWT, password hashing)
├── templates/
│   ├── base.html        # Base template with navbar/footer
│   ├── navbar.html      # Navigation bar component
│   ├── footer.html      # Footer component
│   ├── index.html       # Landing page
│   ├── register.html    # User registration
│   ├── login.html       # User login
│   ├── feed.html        # Main feed with posts
│   ├── post_detail.html # Individual post page
│   ├── profile.html     # User profile page
│   ├── admin_login.html # Admin login page
│   └── admin_dashboard.html # Admin dashboard
├── static/
│   └── css/
│       └── style.css    # Custom CSS styles
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## 🗃️ MongoDB Database Schemas

### Users Collection
```javascript
{
  "_id": ObjectId,
  "username": String (unique, indexed),
  "email": String (unique, indexed),
  "password": String (hashed),
  "profile_pic": String,      // NEW: URL to profile picture
  "followers": [String],      // Array of usernames
  "following": [String],      // Array of usernames
  "created_at": DateTime
}
```

### Posts Collection
```javascript
{
  "_id": ObjectId,
  "author": String (indexed),
  "content": String (max 500 chars),
  "image": String,            // NEW: URL to post image
  "timestamp": DateTime (indexed, descending),
  "likes": [String],          // Array of usernames
  "comments": [
    {
      "username": String,
      "text": String (max 200 chars),
      "timestamp": DateTime
    }
  ]
}
```

### Database Indexes (Auto-created on startup)
```python
# Users collection
db.users.create_index("username", unique=True)
db.users.create_index("email", unique=True)

# Posts collection
db.posts.create_index([("timestamp", -1)])  # Sort by newest
db.posts.create_index("author")             # Filter by author
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB (running on `localhost:27017`)

### Quick Start (Windows)
1. **Test your setup**:
   ```bash
   python test_setup.py
   ```

2. **Start the application**:
   - Double-click `start.bat`, OR
   - Run manually:
     ```bash
     cd backend
     python -m uvicorn backend.main:app --reload --port 8000
     ```

3. **Open browser**: http://localhost:8000

### Manual Setup

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Start MongoDB
Make sure MongoDB is running:
```bash
# Windows (if MongoDB is installed as service)
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
# or
mongod --dbpath /path/to/data/directory
```

#### Step 3: Verify Setup
```bash
python test_setup.py
```
This will check all dependencies, directories, and MongoDB connection.

#### Step 4: Run the Application
```bash
cd backend
python -m uvicorn main:app --reload
```

The app will be available at: **http://localhost:8000**

### 📚 Additional Documentation
- **COMPLETE_GUIDE.md** - Comprehensive feature documentation
- **DEPLOYMENT.md** - Production deployment guide
- **FINAL_SUMMARY.md** - Project completion summary
- **QUICKSTART.md** - Quick setup guide

---

## 🔑 Admin Access

- **URL**: http://localhost:8000/admin/login
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change admin credentials in production by updating `ADMIN_PASSWORD_HASH` in `backend/main.py`

---

## 📚 API Routes

### Authentication
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home page |
| GET | `/register` | Registration page |
| POST | `/register` | Create new user |
| GET | `/login` | Login page |
| POST | `/login` | User login |
| GET | `/logout` | Logout user |

### Posts
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/feed` | View personalized feed |
| POST | `/posts/create` | Create new post (with optional image) |
| GET | `/posts/{post_id}` | View individual post |
| POST | `/posts/{post_id}/like` | Like/unlike post |
| POST | `/posts/{post_id}/comment` | Add comment |

### Profile & Followers
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/profile/{username}` | View user profile |
| POST | `/follow/{username}` | Follow user |
| POST | `/unfollow/{username}` | Unfollow user |
| POST | `/profile/upload-picture` | Upload/change profile picture |

### Admin
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin/login` | Admin login page |
| POST | `/admin/login` | Admin authentication |
| GET | `/admin/dashboard` | Admin dashboard |
| POST | `/admin/users/{user_id}/delete` | Delete user |
| POST | `/admin/posts/{post_id}/delete` | Delete post |
| GET | `/admin/logout` | Admin logout |

---

## 🎯 Usage Examples

### Creating a Post
1. Login to your account
2. Go to `/feed`
3. Type your content (max 500 characters)
4. Click "Post"

### Following a User
1. Visit their profile: `/profile/{username}`
2. Click "Follow" button
3. Their posts will appear in your feed

### Admin Tasks
1. Login at `/admin/login`
2. View statistics on dashboard
3. Manage users and posts
4. Delete inappropriate content

---

## ⚡ Performance Optimizations

### Database Optimizations
1. **Indexes**: Added indexes on frequently queried fields
   - `username` and `email` for user lookups
   - `timestamp` for sorting posts
   - `author` for filtering posts

2. **Projection**: Only fetch required fields
   ```python
   # Example: Exclude password from user queries
   db.users.find({}, {"password": 0})
   ```

3. **Pagination**: Limit results to prevent large data transfers
   ```python
   # Limit to 50 posts
   db.posts.find().limit(50)
   ```

4. **Aggregation Pipeline**: Efficient statistics queries
   ```python
   # Get most liked posts
   db.posts.aggregate([
       {"$project": {"like_count": {"$size": "$likes"}}},
       {"$sort": {"like_count": -1}},
       {"$limit": 5}
   ])
   ```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB (Motor async driver) |
| **Frontend** | Bootstrap 5 + HTML + Jinja2 |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | Bcrypt |
| **Image Processing** | Pillow (PIL) |
| **Server** | Uvicorn (ASGI) |

---

## 📖 Code Examples

### Creating a New Route (Example)
```python
# backend/main.py

@app.get("/custom-route")
async def custom_route(request: Request):
    username = get_current_user(request)
    if not username:
        return RedirectResponse("/login")
    
    # Your logic here
    return templates.TemplateResponse("custom.html", {
        "request": request,
        "username": username
    })
```

### Adding a MongoDB Query (Example)
```python
db = get_database()

# Find all posts by a user
posts = await db.posts.find({"author": username}).to_list(100)

# Update a post
await db.posts.update_one(
    {"_id": ObjectId(post_id)},
    {"$set": {"content": new_content}}
)

# Delete a post
await db.posts.delete_one({"_id": ObjectId(post_id)})
```

---

## 🐛 Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod --version`
- Check connection string in `backend/database.py`

### Port Already in Use
```bash
# Change port when starting
uvicorn main:app --port 8001
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🔄 Future Enhancements

- [ ] Direct messaging between users
- [ ] Image/video upload for posts
- [ ] Hashtags and trending topics
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Real-time notifications
- [ ] Dark mode toggle

---

## 📝 License

This project is created for educational purposes. Feel free to modify and use it for learning.

---

## 👨‍💻 Developer Notes

### Running in Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Database Queries
```python
# Use MongoDB Shell
mongosh
use peopleconnects
db.users.find()
db.posts.find().sort({timestamp: -1})
```

### Resetting Database
```javascript
// In MongoDB Shell
use peopleconnects
db.users.deleteMany({})
db.posts.deleteMany({})
```

---

## 📞 Support

For issues or questions:
1. Check this README thoroughly
2. Review the code comments in `backend/` files
3. Verify MongoDB is running and accessible
4. Check FastAPI logs in terminal

---

**Happy Coding! 🚀**
