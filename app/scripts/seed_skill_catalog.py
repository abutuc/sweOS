from app.db.session import SessionLocal
from app.db.seeds import seed_skill_catalog


def main() -> int:
    db = SessionLocal()
    try:
        return seed_skill_catalog(db)
    finally:
        db.close()


if __name__ == "__main__":
    created_count = main()
    print(f"Seeded {created_count} skill catalog entries.")
