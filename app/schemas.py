"""
Pydantic schemas for request/response validation.

"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRegister(BaseModel):
    
    email: EmailStr  
    username: str    
    password: str    


class UserLogin(BaseModel):
   
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    
    id: int
    email: str
    username: str
    created_at: datetime
    
    # config tells Pydantic to accept SQLAlchemy models directly
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    
    access_token: str
    token_type: str
    user: UserResponse


class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):

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