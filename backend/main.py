"""
FastAPI Main Application - PeopleConnects
"""
from fastapi import FastAPI, Request, HTTPException, Depends, Form, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional
from bson import ObjectId
import shutil
import uuid
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Ensure backend absolute imports work when running this module directly
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load environment variables
load_dotenv()

from backend.database import connect_to_mongo, close_mongo_connection, get_database
from backend.models import UserCreate, UserLogin, PostCreate, CommentCreate, AdminLogin
from backend.auth import hash_password, verify_password, create_access_token
from backend.image_utils import optimize_image

app = FastAPI(title="PeopleConnects")

# Static files and templates

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Admin credentials (in production, store these securely)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = hash_password(os.getenv("ADMIN_PASSWORD"))

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Helper function to get current user from cookie
def get_current_user(request: Request) -> Optional[str]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    from backend.auth import decode_token
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None

# Helper function to save uploaded file
async def save_upload_file(upload_file: UploadFile, upload_dir: str) -> str:
    """Save uploaded file and return filename"""
    if not upload_file:
        return None
    
    # Generate unique filename
    file_extension = upload_file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = BASE_DIR / "static" / "uploads" / upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    # Optimize image (reduce size and quality)
    optimize_image(file_path, max_width=1200, max_height=1200, quality=85)
    
    return f"/static/uploads/{upload_dir}/{unique_filename}"

# ==================== HOME & AUTH ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    username = get_current_user(request)
    
    # If user is logged in, redirect to feed
    if username:
        return RedirectResponse("/feed", status_code=303)
    
    # If not logged in, show login/signup page
    return templates.TemplateResponse("index.html", {"request": request, "username": None})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = None):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": error
    })

@app.post("/register")
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    db = get_database()
    
    # Check if user exists
    existing_user = await db.users.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        # Check which field is duplicate
        if existing_user.get("username") == username:
            error_msg = "Username already taken. Please choose a different username."
        else:
            error_msg = "Email already registered. Please use a different email or login."
        
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error_msg,
            "username": username,
            "email": email
        })
    
    # Create new user
    user_data = {
        "username": username,
        "email": email,
        "password": hash_password(password),
        "profile_pic": None,  # Default: no profile picture
        "followers": [],
        "following": [],
        "created_at": datetime.utcnow()
    }
    await db.users.insert_one(user_data)
    
    # Redirect to login with success message
    return RedirectResponse("/login?registered=true", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None, registered: bool = False):
    success_msg = "Registration successful! Please login." if registered else None
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
        "success": success_msg
    })

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = get_database()
    
    user = await db.users.find_one({"username": username})
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Username not found. Please check your username or register.",
            "username": username
        })
    
    if not verify_password(password, user["password"]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect password. Please try again.",
            "username": username
        })
    
    token = create_access_token({"sub": username})
    response = RedirectResponse("/feed", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response

# ==================== FEED & POSTS ROUTES ====================

@app.get("/feed", response_class=HTMLResponse)
async def feed(request: Request, filter: str = None):
    username = get_current_user(request)
    if not username:
        return RedirectResponse("/login")
    
    db = get_database()
    
    # Get user data for following filter
    user = await db.users.find_one({"username": username})
    following = user.get("following", [])
    
    # Apply filters
    if filter == "following":
        # Show posts only from users you follow
        if following:
            query = {"author": {"$in": following + [username]}}
        else:
            query = {"author": username}
        posts = await db.posts.find(query).sort("timestamp", -1).limit(100).to_list(100)
    
    elif filter == "popular":
        # Show most liked posts (sorted by like count)
        posts = await db.posts.aggregate([
            {"$addFields": {"like_count": {"$size": "$likes"}}},
            {"$sort": {"like_count": -1, "timestamp": -1}},
            {"$limit": 100}
        ]).to_list(100)
    
    elif filter == "recent":
        # Show posts from last 24 hours only
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        posts = await db.posts.find({"timestamp": {"$gte": yesterday}}).sort("timestamp", -1).limit(100).to_list(100)
    
    else:
        # Default: All posts (global feed)
        posts = await db.posts.find({}).sort("timestamp", -1).limit(100).to_list(100)
    
    # Format posts and fetch author profile pictures
    for post in posts:
        post["id"] = str(post["_id"])
        post["liked"] = username in post.get("likes", [])
        post["like_count"] = len(post.get("likes", []))
        post["comment_count"] = len(post.get("comments", []))
        
        # Fetch author's profile picture
        author_user = await db.users.find_one({"username": post["author"]}, {"profile_pic": 1})
        post["author_pfp"] = author_user.get("profile_pic") if author_user else None
    
    return templates.TemplateResponse("feed.html", {
        "request": request, 
        "username": username,
        "posts": posts,
        "filter": filter
    })

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    username = get_current_user(request)
    if not username:
        return RedirectResponse("/login")
    
    db = get_database()
    
    # Search query (case-insensitive)
    query = q.strip()
    
    # Search users by username or email
    users = []
    if query:
        users = await db.users.find({
            "$or": [
                {"username": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}}
            ]
        }, {"password": 0}).limit(20).to_list(20)
        
        # Add follower/following counts
        for user in users:
            user["followers_count"] = len(user.get("followers", []))
            user["following_count"] = len(user.get("following", []))
    
    # Search posts by content
    posts = []
    if query:
        posts = await db.posts.find({
            "content": {"$regex": query, "$options": "i"}
        }).sort("timestamp", -1).limit(20).to_list(20)
        
        # Format posts
        for post in posts:
            post["id"] = str(post["_id"])
            post["liked"] = username in post.get("likes", [])
            post["like_count"] = len(post.get("likes", []))
            post["comment_count"] = len(post.get("comments", []))
            
            # Fetch author profile picture
            author_user = await db.users.find_one({"username": post["author"]}, {"profile_pic": 1})
            post["author_pfp"] = author_user.get("profile_pic") if author_user else None
    
    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "username": username,
        "query": query,
        "users": users,
        "posts": posts
    })

@app.post("/posts/create")
async def create_post(
    request: Request, 
    content: str = Form(...), 
    image: Optional[UploadFile] = File(None)
):
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    
    # Save image if provided
    image_url = None
    if image and image.filename:
        image_url = await save_upload_file(image, "posts")
    
    post_data = {
        "author": username,
        "content": content,
        "image": image_url,
        "timestamp": datetime.utcnow(),
        "likes": [],
        "comments": []
    }
    await db.posts.insert_one(post_data)
    return RedirectResponse("/feed", status_code=303)

@app.get("/posts/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: str):
    username = get_current_user(request)
    if not username:
        return RedirectResponse("/login")
    
    db = get_database()
    
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post["id"] = str(post["_id"])
    post["liked"] = username in post.get("likes", [])
    post["like_count"] = len(post.get("likes", []))
    
    # Fetch author's profile picture
    author_user = await db.users.find_one({"username": post["author"]}, {"profile_pic": 1})
    post["author_pfp"] = author_user.get("profile_pic") if author_user else None
    
    # Fetch profile pictures for commenters
    for comment in post.get("comments", []):
        commenter = await db.users.find_one({"username": comment["username"]}, {"profile_pic": 1})
        comment["user_pfp"] = commenter.get("profile_pic") if commenter else None
    
    return templates.TemplateResponse("post_detail.html", {
        "request": request,
        "username": username,
        "post": post
    })

@app.post("/posts/{post_id}/like")
async def like_post(request: Request, post_id: str):
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    likes = post.get("likes", [])
    if username in likes:
        # Unlike - Toggle off
        await db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$pull": {"likes": username}}
        )
    else:
        # Like - Toggle on
        await db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$addToSet": {"likes": username}}
        )
    
    # Redirect back to referring page (feed or post detail)
    referer = request.headers.get("referer", f"/posts/{post_id}")
    if "/feed" in referer:
        return RedirectResponse("/feed", status_code=303)
    else:
        return RedirectResponse(f"/posts/{post_id}", status_code=303)

@app.post("/posts/{post_id}/comment")
async def add_comment(request: Request, post_id: str, text: str = Form(...)):
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    
    comment = {
        "username": username,
        "text": text,
        "timestamp": datetime.utcnow()
    }
    
    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}}
    )
    
    return RedirectResponse(f"/posts/{post_id}", status_code=303)

@app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_page(request: Request, post_id: str):
    username = get_current_user(request)
    if not username:
        return RedirectResponse("/login")

    db = get_database()
    post = await db.posts.find_one({"_id": ObjectId(post_id)})

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post["author"] != username:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this post")

    post["id"] = str(post["_id"])
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post, "username": username})

@app.post("/posts/{post_id}/edit")
async def edit_post(request: Request, post_id: str, content: str = Form(...)):
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = get_database()
    post = await db.posts.find_one({"_id": ObjectId(post_id)})

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post["author"] != username:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this post")

    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"content": content}}
    )

    return RedirectResponse(f"/posts/{post_id}", status_code=303)

@app.post("/posts/{post_id}/delete")
async def delete_post(request: Request, post_id: str):
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = get_database()
    post = await db.posts.find_one({"_id": ObjectId(post_id)})

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post["author"] != username:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this post")

    await db.posts.delete_one({"_id": ObjectId(post_id)})

    return RedirectResponse("/feed", status_code=303)

# ==================== PROFILE & FOLLOWER ROUTES ====================

@app.get("/profile/{username}", response_class=HTMLResponse)
async def profile(request: Request, username: str):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login")
    
    db = get_database()
    
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's posts
    posts = await db.posts.find({"author": username}).sort("timestamp", -1).limit(20).to_list(20)
    for post in posts:
        post["id"] = str(post["_id"])
        post["like_count"] = len(post.get("likes", []))
        post["comment_count"] = len(post.get("comments", []))
    
    # Check if current user follows this profile
    is_following = current_user in user.get("followers", [])
    
    # Fetch followers list with user details
    followers_usernames = user.get("followers", [])
    followers_list = []
    if followers_usernames:
        followers_list = await db.users.find(
            {"username": {"$in": followers_usernames}},
            {"username": 1, "email": 1, "profile_pic": 1}
        ).to_list(100)
    
    # Fetch following list with user details
    following_usernames = user.get("following", [])
    following_list = []
    if following_usernames:
        following_list = await db.users.find(
            {"username": {"$in": following_usernames}},
            {"username": 1, "email": 1, "profile_pic": 1}
        ).to_list(100)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_user,  # For navbar
        "current_user": current_user,
        "profile_user": username,
        "profile_pic": user.get("profile_pic"),
        "followers_count": len(user.get("followers", [])),
        "following_count": len(user.get("following", [])),
        "followers_list": followers_list,
        "following_list": following_list,
        "is_following": is_following,
        "is_own_profile": current_user == username,
        "posts": posts
    })

@app.post("/follow/{username}")
async def follow_user(request: Request, username: str):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user == username:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    db = get_database()
    
    # Add username to current_user's following
    await db.users.update_one(
        {"username": current_user},
        {"$addToSet": {"following": username}}
    )
    
    # Add current_user to username's followers
    await db.users.update_one(
        {"username": username},
        {"$addToSet": {"followers": current_user}}
    )
    
    return RedirectResponse(f"/profile/{username}", status_code=303)

@app.post("/unfollow/{username}")
async def unfollow_user(request: Request, username: str):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    
    # Remove username from current_user's following
    await db.users.update_one(
        {"username": current_user},
        {"$pull": {"following": username}}
    )
    
    # Remove current_user from username's followers
    await db.users.update_one(
        {"username": username},
        {"$pull": {"followers": current_user}}
    )
    
    return RedirectResponse(f"/profile/{username}", status_code=303)

@app.post("/profile/upload-picture")
async def upload_profile_picture(request: Request, profile_pic: UploadFile = File(...)):
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif", "image/webp"]
    if profile_pic.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
    
    # Save profile picture
    image_url = await save_upload_file(profile_pic, "profiles")
    
    # Update user's profile picture in database
    await db.users.update_one(
        {"username": username},
        {"$set": {"profile_pic": image_url}}
    )
    
    return RedirectResponse(f"/profile/{username}", status_code=303)

@app.get("/profile/edit", response_class=HTMLResponse)
async def edit_profile_page(request: Request):
    username = get_current_user(request)
    if not username:
        return RedirectResponse("/login")
    
    db = get_database()
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "username": username,
        "email": user.get("email"),
        "profile_pic": user.get("profile_pic")
    })

@app.post("/profile/edit")
async def edit_profile(
    request: Request,
    new_username: str = Form(...),
    email: str = Form(None),
    password: str = Form(None)
):
    current_username = get_current_user(request)
    if not current_username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    
    # Check if new username is already taken (if changed)
    if new_username != current_username:
        existing = await db.users.find_one({"username": new_username})
        if existing:
            return templates.TemplateResponse("edit_profile.html", {
                "request": request,
                "username": current_username,
                "error": "Username already taken. Please choose another."
            })
    
    # Prepare update data
    update_data = {}
    if new_username and new_username != current_username:
        update_data["username"] = new_username
    if email:
        update_data["email"] = email
    if password:
        update_data["password"] = hash_password(password)
    
    # Update user
    if update_data:
        await db.users.update_one(
            {"username": current_username},
            {"$set": update_data}
        )
        
        # If username changed, update all posts and references
        if "username" in update_data:
            await db.posts.update_many(
                {"author": current_username},
                {"$set": {"author": new_username}}
            )
            
            # Update followers/following lists
            await db.users.update_many(
                {"followers": current_username},
                {"$set": {"followers.$": new_username}}
            )
            await db.users.update_many(
                {"following": current_username},
                {"$set": {"following.$": new_username}}
            )
            
            # Update likes
            await db.posts.update_many(
                {"likes": current_username},
                {"$set": {"likes.$": new_username}}
            )
            
            # Update comments
            await db.posts.update_many(
                {"comments.username": current_username},
                {"$set": {"comments.$[elem].username": new_username}},
                array_filters=[{"elem.username": current_username}]
            )
            
            # Create new token with new username
            token = create_access_token({"sub": new_username})
            response = RedirectResponse(f"/profile/{new_username}", status_code=303)
            response.set_cookie(key="access_token", value=token, httponly=True)
            return response
    
    return RedirectResponse(f"/profile/{current_username}", status_code=303)

# ==================== ADMIN ROUTES ====================

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(username: str = Form(...), password: str = Form(...)):
    if username != ADMIN_USERNAME or not verify_password(password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    token = create_access_token({"sub": username, "role": "admin"})
    response = RedirectResponse("/admin/dashboard", status_code=303)
    response.set_cookie(key="admin_token", value=token, httponly=True)
    return response

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse("/admin/login")
    
    from backend.auth import decode_token
    payload = decode_token(token)
    if not payload or payload.get("role") != "admin":
        return RedirectResponse("/admin/login")
    
    db = get_database()
    
    # Get statistics
    total_users = await db.users.count_documents({})
    total_posts = await db.posts.count_documents({})
    
    # Get most liked posts
    most_liked_posts = await db.posts.aggregate([
        {"$project": {"author": 1, "content": 1, "like_count": {"$size": "$likes"}}},
        {"$sort": {"like_count": -1}},
        {"$limit": 5}
    ]).to_list(5)
    
    for post in most_liked_posts:
        post["id"] = str(post["_id"])
    
    # Get all users
    users = await db.users.find({}, {"password": 0}).limit(50).to_list(50)
    for user in users:
        user["id"] = str(user["_id"])
    
    # Get all posts
    posts = await db.posts.find({}).sort("timestamp", -1).limit(50).to_list(50)
    for post in posts:
        post["id"] = str(post["_id"])
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "username": payload.get("sub"),  # For navbar
        "total_users": total_users,
        "total_posts": total_posts,
        "most_liked_posts": most_liked_posts,
        "users": users,
        "posts": posts
    })

@app.post("/admin/users/{user_id}/delete")
async def admin_delete_user(request: Request, user_id: str):
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    
    # Delete user and their posts
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.posts.delete_many({"author": user_id})
    
    return RedirectResponse("/admin/dashboard", status_code=303)

@app.post("/admin/posts/{post_id}/delete")
async def admin_delete_post(request: Request, post_id: str):
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = get_database()
    await db.posts.delete_one({"_id": ObjectId(post_id)})
    
    return RedirectResponse("/admin/dashboard", status_code=303)

@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("admin_token")
    return response
