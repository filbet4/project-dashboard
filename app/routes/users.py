"""
User routes: Registration and Login endpoints.

These endpoints handle:
- POST /users/register - Create a new user account
- POST /users/login - Authenticate and get a token
- GET /users/me - Get current authenticated user info
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.auth import hash_password, verify_password, create_access_token, decode_token

# Create router - groups related endpoints together
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Request body:
    {
        "email": "user@example.com",
        "username": "john_doe",
        "password": "secure_password"
    }
    
    Returns:
        The created user (without password)
        
    Raises:
        400: If email or username already exists
    """
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash the password before storing
    hashed_pwd = hash_password(user_data.password)
    
    # Create new user in database
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get authentication token.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "secure_password"
    }
    
    Returns:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "token_type": "bearer",
            "user": {...}
        }
        
    Raises:
        401: If email not found or password incorrect
    """
    
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Check if user exists AND password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """
    Get the current authenticated user's info.
    
    Client should pass the token in the Authorization header:
    Authorization: Bearer <token>
    
    For now, accepts token as query parameter for testing.
    
    Returns:
        The current user's info
        
    Raises:
        401: If token is missing or invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    # Remove quotes if user copy-pasted token with quotes
    # (helps when manually testing and user includes JSON quotes)
    token = token.strip('"').strip("'")
    
    # Decode token to get user_id
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = int(payload["sub"])
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
