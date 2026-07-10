"""
Pydantic schemas for request/response validation.

These define what data clients send us and what we send back.
Pydantic automatically:
- Validates incoming data
- Converts data types
- Generates API documentation
- Sends helpful error messages if validation fails
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRegister(BaseModel):
    """
    Request schema for user registration.
    
    Clients send this JSON to create an account:
    {
        "email": "user@example.com",
        "username": "john_doe",
        "password": "secure_password123"
    }
    """
    email: EmailStr  # Validates it's a real email format
    username: str    # Just a string
    password: str    # Will be hashed before storing


class UserLogin(BaseModel):
    """
    Request schema for login.
    
    Clients send:
    {
        "email": "user@example.com",
        "password": "secure_password123"
    }
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Response schema - what we send back when queried about a user.
    
    We send this (notice: no password!):
    {
        "id": 1,
        "email": "user@example.com",
        "username": "john_doe",
        "created_at": "2026-07-02T10:30:00"
    }
    """
    id: int
    email: str
    username: str
    created_at: datetime
    
    # config tells Pydantic to accept SQLAlchemy models directly
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Response schema for login endpoint.
    
    After successful login, we send:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "user@example.com",
            ...
        }
    }
    """
    access_token: str
    token_type: str
    user: UserResponse


class ProjectCreate(BaseModel):
    """Request schema for creating a project."""
    name: str
    description: str


class ProjectUpdate(BaseModel):
    """Request schema for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Response schema for project data."""
    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    """
    Response schema returned after uploading or listing documents.
    """

    id: int

    filename: str

    content_type: str

    project_id: int

    uploaded_at: datetime

    class Config:
        from_attributes = True

class MemberRole(str, Enum):
    OWNER = "OWNER"
    PARTICIPANT = "PARTICIPANT"

class MemberInvite(BaseModel):
    email: EmailStr

class MemberResponse(BaseModel):

    id: int

    user_id: int

    project_id: int

    role: MemberRole

    created_at: datetime

    class Config:
        from_attributes = True