from app.core.bootstrap import get_or_create_default_user
from app.db.metadata import Base
from app.db.seeds import seed_skill_catalog
from app.db.session import SessionLocal, engine


def main() -> dict[str, object]:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        user = get_or_create_default_user(db)
        created_skills = seed_skill_catalog(db)
        return {
            "user_email": user.email,
            "created_skills": created_skills,
        }
    finally:
        db.close()


if __name__ == "__main__":
    result = main()
    print(
        f"Bootstrapped Epic 1 data for {result['user_email']} "
        f"with {result['created_skills']} new skills."
    )
