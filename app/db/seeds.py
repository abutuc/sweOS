from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.skill import Skill


DEFAULT_SKILLS: Sequence[dict[str, str]] = (
    {
        "slug": "python",
        "name": "Python",
        "category": "language",
        "description": "General-purpose programming language.",
    },
    {
        "slug": "java",
        "name": "Java",
        "category": "language",
        "description": "Object-oriented language for backend systems.",
    },
    {
        "slug": "fastapi",
        "name": "FastAPI",
        "category": "framework",
        "description": "Python web framework for APIs.",
    },
    {
        "slug": "postgresql",
        "name": "PostgreSQL",
        "category": "database",
        "description": "Relational database and ecosystem.",
    },
    {
        "slug": "docker",
        "name": "Docker",
        "category": "cloud-devops",
        "description": "Containerization platform.",
    },
    {
        "slug": "system-design",
        "name": "System Design",
        "category": "architecture",
        "description": "Designing scalable and reliable systems.",
    },
    {
        "slug": "distributed-systems",
        "name": "Distributed Systems",
        "category": "architecture",
        "description": "Concepts for operating across multiple services or nodes.",
    },
    {
        "slug": "algorithms",
        "name": "Algorithms",
        "category": "computer-science",
        "description": "Algorithmic problem-solving and complexity analysis.",
    },
)


def seed_skill_catalog(db: Session) -> int:
    created_count = 0

    for skill_data in DEFAULT_SKILLS:
        existing_skill = db.query(Skill).filter(Skill.slug == skill_data["slug"]).one_or_none()
        if existing_skill is not None:
            continue

        db.add(Skill(**skill_data))
        created_count += 1

    db.commit()
    return created_count
