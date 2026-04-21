from sqlalchemy.orm import Session

from app.models.user import User


DEFAULT_USER_EMAIL = "default@sweos.local"


def get_or_create_default_user(db: Session) -> User:
    user = db.query(User).filter(User.email == DEFAULT_USER_EMAIL).one_or_none()
    if user is not None:
        return user

    user = User(
        email=DEFAULT_USER_EMAIL,
        password_hash="disabled",
        full_name="Default User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
