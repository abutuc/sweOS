import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import skills as skills_api
from app.api.dependencies import get_db_session, require_current_user
from app.main import app
from app.models.user_skill import ProficiencyLevel


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

    def in_(self, values):
        return _Predicate(lambda obj: getattr(obj, self.field_name) in values)

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


def test_get_skills_catalog_filters_by_search_term():
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
        response = client.get("/api/v1/skills/catalog", params={"search": "post"})

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


class _FakeUserSkillQuery:
    def __init__(self, user_skills):
        self._user_skills = user_skills

    def filter(self, *predicates):
        filtered = []
        for user_skill in self._user_skills:
            if all(predicate.compare(user_skill) for predicate in predicates):
                filtered.append(user_skill)
        return _FakeUserSkillQuery(filtered)

    def all(self):
        return self._user_skills

    def one_or_none(self):
        if not self._user_skills:
            return None
        return self._user_skills[0]


class _FakeUserSkillModel:
    user_id = _FakeColumn("user_id")


class _FakeUserSkillSession:
    def __init__(self, user_skills, existing_skill_ids=None):
        self._user_skills = user_skills
        self._existing_skill_ids = list(existing_skill_ids or [])
        self.committed = False

    def query(self, *args, **_kwargs):
        if args and getattr(args[0], "field_name", None) == "skill_id":
            return _FakeSkillIdQuery(self._existing_skill_ids)
        return _FakeUserSkillQuery(self._user_skills)

    def add(self, obj):
        self._user_skills.append(obj)

    def commit(self):
        self.committed = True

    def close(self):
        return None


class _FakeSkillIdQuery:
    def __init__(self, skill_ids):
        self._skill_ids = skill_ids

    def filter(self, predicate):
        return _FakeSkillIdQuery(
            [skill_id for skill_id in self._skill_ids if predicate.compare(SimpleNamespace(skill_id=skill_id))]
        )

    def all(self):
        return [(skill_id,) for skill_id in self._skill_ids]


def _override_current_user(user_id: uuid.UUID):
    def _override():
        return SimpleNamespace(id=user_id)

    return _override


def test_get_my_skills_returns_structured_skill_entries():
    user_id = uuid.uuid4()
    skill_id = uuid.uuid4()
    evaluated_at = datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc)

    fake_session = _FakeUserSkillSession(
        [
            SimpleNamespace(
                user_id=user_id,
                skill=SimpleNamespace(
                    id=skill_id,
                    slug="python",
                    name="Python",
                    category="language",
                ),
                self_assessed_level=ProficiencyLevel.advanced,
                measured_level=ProficiencyLevel.intermediate,
                confidence_score=Decimal("0.74"),
                evidence_count=8,
                last_evaluated_at=evaluated_at,
            )
        ]
    )

    def override_get_db_session():
        yield fake_session

    original_user_skill_model = skills_api.UserSkill
    skills_api.UserSkill = _FakeUserSkillModel
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.get("/api/v1/skills/me")

    skills_api.UserSkill = original_user_skill_model
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "skillId": str(skill_id),
                "skillSlug": "python",
                "skillName": "Python",
                "category": "language",
                "selfAssessedLevel": "advanced",
                "measuredLevel": "intermediate",
                "confidenceScore": "0.74",
                "evidenceCount": 8,
                "lastEvaluatedAt": "2026-04-22T10:00:00Z",
            }
        ]
    }


def test_put_my_skills_creates_and_updates_user_skills():
    user_id = uuid.uuid4()
    existing_skill_id = uuid.uuid4()
    new_skill_id = uuid.uuid4()

    existing_user_skill = SimpleNamespace(
        user_id=user_id,
        skill_id=existing_skill_id,
        self_assessed_level=ProficiencyLevel.beginner,
    )
    fake_session = _FakeUserSkillSession(
        [existing_user_skill],
        existing_skill_ids=[existing_skill_id, new_skill_id],
    )

    def override_get_db_session():
        yield fake_session

    original_user_skill_model = skills_api.UserSkill
    original_skill_model = skills_api.Skill

    class _FakeWritableUserSkillModel(_FakeUserSkillModel):
        skill_id = _FakeColumn("skill_id")

        def __init__(self, user_id, skill_id, self_assessed_level):
            self.user_id = user_id
            self.skill_id = skill_id
            self.self_assessed_level = self_assessed_level

    class _FakeSkillModel:
        id = _FakeColumn("skill_id")

    skills_api.UserSkill = _FakeWritableUserSkillModel
    skills_api.Skill = _FakeSkillModel
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/skills/me",
            json={
                "skills": [
                    {
                        "skill_id": str(existing_skill_id),
                        "self_assessed_level": "advanced",
                    },
                    {
                        "skill_id": str(new_skill_id),
                        "self_assessed_level": "intermediate",
                    },
                ]
            },
        )

    skills_api.UserSkill = original_user_skill_model
    skills_api.Skill = original_skill_model
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"data": {"updatedCount": 2}}
    assert fake_session.committed is True
    assert existing_user_skill.self_assessed_level == ProficiencyLevel.advanced
    created_user_skill = next(
        user_skill for user_skill in fake_session._user_skills if user_skill.skill_id == new_skill_id
    )
    assert created_user_skill.user_id == user_id
    assert created_user_skill.self_assessed_level == ProficiencyLevel.intermediate


def test_put_my_skills_rejects_duplicate_skill_ids():
    user_id = uuid.uuid4()
    fake_session = _FakeUserSkillSession([])

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    duplicate_skill_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/skills/me",
            json={
                "skills": [
                    {
                        "skillId": str(duplicate_skill_id),
                        "selfAssessedLevel": "advanced",
                    },
                    {
                        "skillId": str(duplicate_skill_id),
                        "selfAssessedLevel": "intermediate",
                    },
                ]
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert fake_session.committed is False


def test_put_my_skills_rejects_unknown_skill_ids():
    user_id = uuid.uuid4()
    unknown_skill_id = uuid.uuid4()
    fake_session = _FakeUserSkillSession([], existing_skill_ids=[])

    def override_get_db_session():
        yield fake_session

    original_skill_model = skills_api.Skill

    class _FakeSkillModel:
        id = _FakeColumn("skill_id")

    skills_api.Skill = _FakeSkillModel
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/skills/me",
            json={
                "skills": [
                    {
                        "skillId": str(unknown_skill_id),
                        "selfAssessedLevel": "advanced",
                    }
                ]
            },
        )

    skills_api.Skill = original_skill_model
    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "Unknown skillId values" in response.json()["detail"]
    assert fake_session.committed is False
