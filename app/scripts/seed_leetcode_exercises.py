from app.db.leetcode_catalog import LEETCODE_PROBLEMS
from app.db.seeds import seed_leetcode_exercises
from app.db.session import SessionLocal


def main() -> int:
    db = SessionLocal()
    try:
        return seed_leetcode_exercises(db)
    finally:
        db.close()


if __name__ == "__main__":
    created_count = main()
    print(f"Seeded {created_count} LeetCode exercises from {len(LEETCODE_PROBLEMS)} problems.")
