from collections.abc import Generator

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.tokens import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session,
    authorization: str | None,
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except Exception as exc:  # pragma: no cover - normalized to 401
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_current_user(
    db: Session = Depends(get_db_session),
    authorization: str | None = Header(default=None),
) -> User:
    return get_current_user(db, authorization)
