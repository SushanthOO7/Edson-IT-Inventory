from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.security import get_password_hash, verify_password

settings = get_settings()


def ensure_default_admin(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == settings.default_admin_email))
    if user:
        return user
    user = User(
        email=settings.default_admin_email,
        full_name=settings.default_admin_full_name,
        role="ADMIN",
        password_hash=get_password_hash(settings.default_admin_password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
