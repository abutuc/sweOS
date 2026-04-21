from app.db import seeds


class _Predicate:
    def __init__(self, evaluator):
        self._evaluator = evaluator

    def compare(self, obj):
        return self._evaluator(obj)


class _FakeColumn:
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __eq__(self, other):
        return _Predicate(lambda obj: getattr(obj, self.field_name) == other)


class _FakeSkillModel:
    slug = _FakeColumn("slug")

    def __init__(self, slug, name, category, description):
        self.slug = slug
        self.name = name
        self.category = category
        self.description = description


class _FakeQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, predicate):
        return _FakeQuery([item for item in self._items if predicate.compare(item)])

    def one_or_none(self):
        if not self._items:
            return None
        return self._items[0]


class _FakeSession:
    def __init__(self, existing_skills=None):
        self.skills = list(existing_skills or [])
        self.committed = False

    def query(self, *_args, **_kwargs):
        return _FakeQuery(self.skills)

    def add(self, obj):
        self.skills.append(obj)

    def commit(self):
        self.committed = True


def test_seed_skill_catalog_creates_missing_skills(monkeypatch):
    fake_session = _FakeSession()
    monkeypatch.setattr(seeds, "Skill", _FakeSkillModel)

    created_count = seeds.seed_skill_catalog(fake_session)

    assert created_count == len(seeds.DEFAULT_SKILLS)
    assert fake_session.committed is True
    assert {skill.slug for skill in fake_session.skills} == {
        skill_data["slug"] for skill_data in seeds.DEFAULT_SKILLS
    }


def test_seed_skill_catalog_skips_existing_skills(monkeypatch):
    existing_skill = _FakeSkillModel(
        slug="python",
        name="Python",
        category="language",
        description="Existing entry.",
    )
    fake_session = _FakeSession(existing_skills=[existing_skill])
    monkeypatch.setattr(seeds, "Skill", _FakeSkillModel)

    created_count = seeds.seed_skill_catalog(fake_session)

    assert created_count == len(seeds.DEFAULT_SKILLS) - 1
    assert fake_session.committed is True
    assert len([skill for skill in fake_session.skills if skill.slug == "python"]) == 1
