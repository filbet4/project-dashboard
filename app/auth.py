"""
Authentication utilities.

Handles password hashing and JWT token creation/verification.
"""

import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

# JWT configuration from .env
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    
    Example:
        plain = "my_password"
        hashed = hash_password(plain)  # Returns something like: $2b$12$...
        
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password (safe to store in database)
    """
    # Encode password as bytes, bcrypt requires bytes
    password_bytes = password.encode('utf-8')
    # Hash with bcrypt using 10 rounds (default, secure but reasonably fast)
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=10))
    # Return as string for storage in database
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Used during login to check if password is correct.
    
    Example:
        stored_hash = "$2b$12$..."
        user_input = "my_password"
        if verify_password(user_input, stored_hash):
            print("Password is correct!")
    
    Args:
        plain_password: The password the user typed in
        hashed_password: The password hash stored in database
        
    Returns:
        True if password matches, False otherwise
    """
    # Encode both to bytes and compare
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def create_access_token(data: dict) -> str:
    """
    Create a JWT token for authentication.
    
    The token contains encoded data (user_id, expiration, etc).
    Client includes this token in future requests to prove they're authenticated.
    
    Example:
        token = create_access_token({"sub": "user_id_123"})
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi..."
    
    Args:
        data: Dictionary with info to encode in token (usually {"sub": user_id})
        
    Returns:
        A JWT token string
    """
    # Make a copy so we don't modify the original dict
    to_encode = data.copy()
    
    # Set expiration time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode data into JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    
    Used to extract user_id from token and check if it's expired.
    
    Args:
        token: The JWT token string
        
    Returns:
        The decoded token data (dictionary)
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
