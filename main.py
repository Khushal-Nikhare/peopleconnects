
from fastapi import FastAPI, Request, Form, Depends, HTTPException, Response, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bson import ObjectId
import shutil

app = FastAPI()

# --- Database ---
client = MongoClient("mongodb://localhost:27017/")
db = client["peoples_connect"]
users_collection = db["users"]
posts_collection = db["posts"]

# --- Templates ---
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- Helper Functions ---
def get_current_user(request: Request):
    username = request.cookies.get("username")
    if not username:
        return None
    user = users_collection.find_one({"username": username})
    return user

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = get_current_user(request)
    posts = posts_collection.find().sort("timestamp", -1)
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts, "user": user})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    posts = posts_collection.find({"author": user["username"]}).sort("timestamp", -1)
    return templates.TemplateResponse("profile.html", {"request": request, "posts": posts, "user": user})

@app.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    if users_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    users_collection.insert_one({"username": username, "password": password})
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"username": username})
    if not user or user["password"] != password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="username", value=username, httponly=True)
    return response

@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("username")
    return response

@app.post("/posts")
async def create_post(request: Request, content: str = Form(...), photo: UploadFile = File(None)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    photo_filename = None
    if photo and photo.filename:
        photo_filename = f"{user['username']}_{photo.filename}"
        with open(f"uploads/{photo_filename}", "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

    posts_collection.insert_one({
        "author": user["username"],
        "content": content,
        "photo": photo_filename,
        "likes": [],
        "comments": [],
        "timestamp": ""
    })
    return RedirectResponse(url="/", status_code=303)

@app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: str):
    user = get_current_user(request)
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not user or user["username"] != post["author"]:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})

@app.post("/posts/{post_id}/edit")
async def edit_post(request: Request, post_id: str, content: str = Form(...)):
    user = get_current_user(request)
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not user or user["username"] != post["author"]:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")
    posts_collection.update_one({"_id": ObjectId(post_id)}, {"$set": {"content": content}})
    return RedirectResponse(url="/", status_code=303)

@app.post("/posts/{post_id}/delete")
async def delete_post(request: Request, post_id: str):
    user = get_current_user(request)
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not user or user["username"] != post["author"]:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    posts_collection.delete_one({"_id": ObjectId(post_id)})
    return RedirectResponse(url="/", status_code=303)

@app.post("/posts/{post_id}/like")
async def like_post(request: Request, post_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if user["username"] in post["likes"]:
        posts_collection.update_one({"_id": ObjectId(post_id)}, {"$pull": {"likes": user["username"]}})
    else:
        posts_collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"likes": user["username"]}})
    return RedirectResponse(url="/", status_code=303)

@app.post("/posts/{post_id}/comment")
async def comment_on_post(request: Request, post_id: str, comment: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    posts_collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"comments": {"author": user["username"], "text": comment}}})
    return RedirectResponse(url="/", status_code=303)


# Run $ python -m uvicorn main:app --reload