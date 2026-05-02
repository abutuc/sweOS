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

    def filter(self, *predicates):
        return _FakeQuery(
            [item for item in self._items if all(predicate.compare(item) for predicate in predicates)]
        )

    def one_or_none(self):
        if not self._items:
            return None
        return self._items[0]


class _FakeExerciseColumn:
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __eq__(self, other):
        return _Predicate(lambda obj: getattr(obj, self.field_name) == other)

    def is_(self, other):
        return _Predicate(lambda obj: getattr(obj, self.field_name) is other)


class _FakeExerciseModel:
    user_id = _FakeExerciseColumn("user_id")
    title = _FakeExerciseColumn("title")

    def __init__(
        self,
        *,
        user_id,
        type,
        topic,
        subtopic,
        difficulty,
        title,
        prompt_markdown,
        constraints_json,
        expected_outcomes_json,
        hints_json,
        canonical_solution_json,
        tags,
        source,
        created_by_ai,
    ):
        self.user_id = user_id
        self.type = type
        self.topic = topic
        self.subtopic = subtopic
        self.difficulty = difficulty
        self.title = title
        self.prompt_markdown = prompt_markdown
        self.constraints_json = constraints_json
        self.expected_outcomes_json = expected_outcomes_json
        self.hints_json = hints_json
        self.canonical_solution_json = canonical_solution_json
        self.tags = tags
        self.source = source
        self.created_by_ai = created_by_ai


class _FakeSession:
    def __init__(self, existing_skills=None, existing_exercises=None):
        self.skills = list(existing_skills or [])
        self.exercises = list(existing_exercises or [])
        self.committed = False

    def query(self, *_args, **_kwargs):
        model = _args[0] if _args else None
        if model is _FakeSkillModel:
            return _FakeQuery(self.skills)
        if model is _FakeExerciseModel:
            return _FakeQuery(self.exercises)
        return _FakeQuery([])

    def add(self, obj):
        if isinstance(obj, _FakeSkillModel):
            self.skills.append(obj)
        else:
            self.exercises.append(obj)

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


def test_seed_leetcode_exercises_creates_the_catalog(monkeypatch):
    fake_session = _FakeSession()
    monkeypatch.setattr(seeds, "Exercise", _FakeExerciseModel)

    created_count = seeds.seed_leetcode_exercises(fake_session)

    assert created_count == len(seeds.LEETCODE_PROBLEMS)
    assert fake_session.committed is True
    assert len(fake_session.exercises) == len(seeds.LEETCODE_PROBLEMS)


def test_seed_leetcode_exercises_skips_existing_rows(monkeypatch):
    existing_problem = _FakeExerciseModel(
        user_id=None,
        type="dsa",
        topic="arrays",
        subtopic="hash-map lookup",
        difficulty=seeds.LEETCODE_PROBLEMS[0]["difficulty"],
        title=seeds.LEETCODE_PROBLEMS[0]["title"],
        prompt_markdown="Existing entry.",
        constraints_json={},
        expected_outcomes_json=[],
        hints_json=[],
        canonical_solution_json=None,
        tags=["leetcode"],
        source=None,
        created_by_ai=False,
    )
    fake_session = _FakeSession(existing_exercises=[existing_problem])
    monkeypatch.setattr(seeds, "Exercise", _FakeExerciseModel)

    created_count = seeds.seed_leetcode_exercises(fake_session)

    assert created_count == len(seeds.LEETCODE_PROBLEMS) - 1
    assert fake_session.committed is True
