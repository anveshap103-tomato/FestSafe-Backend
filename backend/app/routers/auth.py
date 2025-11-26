"""
Authentication router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.database import get_db
from app.db import crud, models
from app.schemas import auth
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    settings
)

router = APIRouter()


@router.post("/login", response_model=auth.Token)
async def login(
    login_data: auth.LoginRequest,
    db: Session = Depends(get_db)
):
    """Login endpoint."""
    user = crud.get_user_by_email(db, email=login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=auth.User)
async def register(
    user_data: auth.UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if user exists
    existing_user = crud.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    user_dict["hashed_password"] = hashed_password
    user_dict.pop("password")
    
    user = crud.create_user(db, user_dict)
    return user


@router.get("/me", response_model=auth.User)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user


