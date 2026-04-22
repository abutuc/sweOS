# sweOS
sweOS — the operating system for software engineers to learn, practice, and grow in the age of AI

## Local Development

This repository currently contains a FastAPI backend scaffold for Epic 1.

### Requirements

- Python 3.12.9
- Docker and Docker Compose

### Setup

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
docker compose up -d db
sweos-create-tables
sweos-bootstrap-epic1
```

### Run Tests

```bash
.venv/bin/pytest
```

To run a smaller slice while iterating:

```bash
.venv/bin/pytest tests/test_profile_api.py
.venv/bin/pytest tests/test_skills_api.py
.venv/bin/pytest tests/test_seeds.py
.venv/bin/pytest tests/test_bootstrap.py
```

To surface current schema warnings explicitly during API test cleanup:

```bash
.venv/bin/pytest tests/test_profile_api.py tests/test_skills_api.py -W default
```

### Bootstrap Utilities

After the editable install, these commands are available:

```bash
sweos-create-tables
sweos-seed-default-user
sweos-seed-skill-catalog
sweos-bootstrap-epic1
```

### Migrations

Apply the current schema revision:

```bash
.venv/bin/alembic upgrade head
```

Roll the schema back one revision:

```bash
.venv/bin/alembic downgrade -1
```

### Integration Tests

Integration tests expect Postgres to be reachable at the configured `database_url`.
If the database is unavailable, the integration suite will skip cleanly.
Because the current integration setup shares one database, run these slices sequentially rather than in parallel.

```bash
.venv/bin/pytest -m integration
.venv/bin/pytest tests/test_migrations.py -m integration
.venv/bin/pytest tests/test_profile_integration.py -m integration
.venv/bin/pytest tests/test_skills_integration.py -m integration
.venv/bin/pytest tests/test_goals_integration.py -m integration
```
