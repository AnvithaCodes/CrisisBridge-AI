"""
Shared Dependencies for CrisisBridge AI
=========================================
FastAPI dependency injection functions used across ALL routes.

Usage in any route file:
    from shared.dependencies import get_db, get_current_user, get_redis

    @router.get("/items")
    async def get_items(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
        redis = Depends(get_redis),
    ):
        ...
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import redis as redis_lib

from shared.config import settings
from shared.database import SessionLocal
from shared.models import User
from shared.enums import UserRole


# ── Security scheme ──────────────────────────────
security = HTTPBearer()


# ═══════════════════════════════════════════════════
#  DATABASE DEPENDENCY
#  Used by: ALL
# ═══════════════════════════════════════════════════

def get_db() -> Generator[Session, None, None]:
    """
    Yields a database session per request.
    Automatically closes after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════
#  REDIS DEPENDENCY
#  Used by: Person 3 (caching), Person 2 (session memory)
# ═══════════════════════════════════════════════════

# Singleton Redis connection pool
_redis_pool: Optional[redis_lib.ConnectionPool] = None


def _get_redis_pool() -> redis_lib.ConnectionPool:
    """Create or return existing Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis_lib.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
    return _redis_pool


def get_redis() -> redis_lib.Redis:
    """
    Returns a Redis client using the shared connection pool.
    Use for caching, session storage, and pub/sub.
    """
    pool = _get_redis_pool()
    return redis_lib.Redis(connection_pool=pool)


# ═══════════════════════════════════════════════════
#  AUTH DEPENDENCIES
#  Used by: ALL (route protection)
# ═══════════════════════════════════════════════════

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Extracts and validates the JWT token from the Authorization header.
    Returns the current User ORM object.
    Raises 401 if token is invalid or user not found.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Alias that ensures the user is active."""
    return current_user


# ── Role-based access control helpers ────────────

def require_role(*allowed_roles: UserRole):
    """
    Dependency factory: restricts endpoint to specific roles.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker


# ── Optional auth (for endpoints accessible by anonymous users too) ────

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Like get_current_user but returns None instead of 401 if no token.
    Useful for endpoints that work for both logged-in and anonymous users.
    """
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
