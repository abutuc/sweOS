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
