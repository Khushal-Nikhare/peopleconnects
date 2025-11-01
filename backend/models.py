"""
Pydantic Models for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    profile_pic: Optional[str] = None
    followers: List[str] = []
    following: List[str] = []
    
class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=200)

class PostResponse(BaseModel):
    id: str
    author: str
    content: str
    image: Optional[str] = None
    timestamp: datetime
    likes: List[str] = []
    comments: List[dict] = []
    
class AdminLogin(BaseModel):
    username: str
    password: str
