from app.core.bootstrap import get_or_create_default_user
from app.db.session import SessionLocal


def main():
    db = SessionLocal()
    try:
        return get_or_create_default_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    user = main()
    print(f"Ready default user: {user.email}")
