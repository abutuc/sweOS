from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.core.security import hash_password, verify_password
from app.core.tokens import create_access_token
from app.models.user import User
from app.schemas.auth import (
    AuthEnvelope,
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthResponseData,
    AuthUser,
    AuthUserEnvelope,
    AuthUserUpdateRequest,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthEnvelope)
def register(
    payload: AuthRegisterRequest,
    db: Session = Depends(get_db_session),
) -> AuthEnvelope:
    existing_user = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    return AuthEnvelope(
        data=AuthResponseData(
            user=AuthUser.model_validate(user),
            token=token,
        )
    )


@router.post("/login", response_model=AuthEnvelope)
def login(
    payload: AuthLoginRequest,
    db: Session = Depends(get_db_session),
) -> AuthEnvelope:
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user.id))
    return AuthEnvelope(
        data=AuthResponseData(
            user=AuthUser.model_validate(user),
            token=token,
        )
    )


@router.get("/me", response_model=AuthUserEnvelope)
def get_me(user: User = Depends(require_current_user)) -> AuthUserEnvelope:
    return AuthUserEnvelope(data=AuthUser.model_validate(user))


@router.put("/me", response_model=AuthUserEnvelope)
def update_me(
    payload: AuthUserUpdateRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> AuthUserEnvelope:
    user.full_name = payload.full_name
    db.commit()
    db.refresh(user)
    return AuthUserEnvelope(data=AuthUser.model_validate(user))
