"""
Authentication API routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    APIResponse,
    AuthResponse,
    AuthUserResponse,
    LoginRequest,
    RefreshResponse,
    RefreshTokenRequest,
    RegisterRequest,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Returns user data and JWT tokens on success.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return APIResponse.error_response(
            code="VALIDATION_EMAIL_EXISTS",
            message="Email already registered",
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        name=request.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return APIResponse.success_response(
        AuthResponse(
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )
    )


@router.post(
    "/login",
    response_model=APIResponse[AuthResponse],
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return APIResponse.error_response(
            code="AUTH_INVALID_CREDENTIALS",
            message="Invalid email or password",
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        return APIResponse.error_response(
            code="AUTH_INVALID_CREDENTIALS",
            message="Invalid email or password",
        )

    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return APIResponse.success_response(
        AuthResponse(
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )
    )


@router.post(
    "/refresh",
    response_model=APIResponse[RefreshResponse],
)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using a valid refresh token.
    """
    # Verify refresh token
    user_id = verify_refresh_token(request.refresh_token)
    if user_id is None:
        return APIResponse.error_response(
            code="AUTH_TOKEN_INVALID",
            message="Invalid or expired refresh token",
        )

    # Verify user still exists
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        return APIResponse.error_response(
            code="AUTH_TOKEN_INVALID",
            message="User not found",
        )

    # Generate new access token
    access_token = create_access_token(str(user.id))

    return APIResponse.success_response(RefreshResponse(access_token=access_token))


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    return APIResponse.success_response(
        UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            unit_system=current_user.unit_system,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
        )
    )


@router.patch(
    "/me",
    response_model=APIResponse[UserResponse],
)
async def update_me(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the current authenticated user's profile.
    """
    # Update user fields if provided
    if request.name is not None:
        current_user.name = request.name
    if request.unit_system is not None:
        current_user.unit_system = request.unit_system

    db.commit()
    db.refresh(current_user)

    return APIResponse.success_response(
        UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            unit_system=current_user.unit_system,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
        )
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete the current authenticated user's account.

    This will permanently delete the user and all associated data.
    """
    db.delete(current_user)
    db.commit()
    return None
