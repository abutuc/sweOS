import uuid
from dataclasses import dataclass

from fastapi.testclient import TestClient

from app.api import skills as skills_api
from app.api.dependencies import get_db_session
from app.main import app


class _Predicate:
    def __init__(self, evaluator):
        self._evaluator = evaluator

    def compare(self, obj):
        return self._evaluator(obj)

    def __or__(self, other):
        return _Predicate(lambda obj: self.compare(obj) or other.compare(obj))


class _FakeColumn:
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __eq__(self, other):
        return _Predicate(lambda obj: getattr(obj, self.field_name) == other)

    def ilike(self, pattern: str):
        needle = pattern.strip("%").lower()
        return _Predicate(lambda obj: needle in getattr(obj, self.field_name).lower())

    def asc(self):
        return self


class _FakeSkillModel:
    category = _FakeColumn("category")
    name = _FakeColumn("name")
    slug = _FakeColumn("slug")


@dataclass
class _FakeSkill:
    id: uuid.UUID
    slug: str
    name: str
    category: str
    description: str | None = None


class _FakeSkillQuery:
    def __init__(self, skills: list[_FakeSkill]):
        self._skills = skills

    def filter(self, predicate):
        filtered = []
        for skill in self._skills:
            if predicate.compare(skill):
                filtered.append(skill)
        return _FakeSkillQuery(filtered)

    def order_by(self, *_args, **_kwargs):
        return _FakeSkillQuery(sorted(self._skills, key=lambda skill: skill.name))

    def all(self):
        return self._skills


class _FakeSkillSession:
    def __init__(self, skills: list[_FakeSkill]):
        self._skills = skills

    def query(self, *_args, **_kwargs):
        return _FakeSkillQuery(self._skills)

    def close(self):
        return None


def test_get_skills_catalog_returns_sorted_skills():
    fake_session = _FakeSkillSession(
        [
            _FakeSkill(
                id=uuid.uuid4(),
                slug="python",
                name="Python",
                category="language",
                description="Programming language",
            ),
            _FakeSkill(
                id=uuid.uuid4(),
                slug="postgresql",
                name="PostgreSQL",
                category="database",
                description="Relational database",
            ),
        ]
    )

    def override_get_db_session():
        yield fake_session

    original_skill_model = skills_api.Skill
    skills_api.Skill = _FakeSkillModel
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.get("/api/v1/skills/catalog")

    skills_api.Skill = original_skill_model
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "id": str(fake_session._skills[1].id),
                "slug": "postgresql",
                "name": "PostgreSQL",
                "category": "database",
                "description": "Relational database",
            },
            {
                "id": str(fake_session._skills[0].id),
                "slug": "python",
                "name": "Python",
                "category": "language",
                "description": "Programming language",
            },
        ]
    }


def test_get_skills_catalog_filters_by_category():
    fake_session = _FakeSkillSession(
        [
            _FakeSkill(id=uuid.uuid4(), slug="python", name="Python", category="language"),
            _FakeSkill(
                id=uuid.uuid4(),
                slug="postgresql",
                name="PostgreSQL",
                category="database",
            ),
        ]
    )

    def override_get_db_session():
        yield fake_session

    original_skill_model = skills_api.Skill
    skills_api.Skill = _FakeSkillModel
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.get("/api/v1/skills/catalog", params={"category": "database"})

    skills_api.Skill = original_skill_model
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"] == [
        {
            "id": str(fake_session._skills[1].id),
            "slug": "postgresql",
            "name": "PostgreSQL",
            "category": "database",
            "description": None,
        }
    ]
