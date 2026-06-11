# Python profile

Used by `backend-implementation` when the repo is Python.

## Detection

- `pyproject.toml`, `requirements.txt`, `setup.py`, `setup.cfg`
- Framework: `fastapi`, `flask`, `django`, `starlette`, `aiohttp`
- Data: `sqlalchemy`, `pydantic`, `alembic`, `peewee`
- Async: `celery`, `dramatiq`, `rq`
- Lint / type: `ruff`, `mypy`, `pylint`, `flake8`, `black`,
  `isort` (only if present)
- Test: `pytest`, `pytest-asyncio`, `unittest`, `hypothesis` (only
  if present)
- Task runner: `tox.ini`, `noxfile.py` (informational)

## Architecture

Preserve the existing layering. Common patterns:

- `src/<package>/` or flat `package/`
- `app/` or `project_name/`
- `routes/` / `views/` / `controllers/`
- `services/`
- `models/` / `repositories/`
- `schemas/` (Pydantic) or `serializers/` (DRF)
- `db/` (engine, session, migrations)

Match the existing convention. Do not introduce a new layout.

## Test rules

- pytest if present / configured; unittest if pytest is not present.
- `conftest.py` fixtures — use existing ones; do not add new top-level
  fixtures without recording why.
- Mocking: `unittest.mock` standard; `pytest-mock` (`mocker` fixture)
  only if already used. Do not introduce a new mocking library.
- Do not introduce `ruff`, `mypy`, `pytest-cov`, `pytest-xdist`,
  `hypothesis`, etc. unless already present or explicitly approved.

## Migration rules

- Alembic: do not write destructive migrations. Use
  `database-migration-safety` first.
- Django: do not run `makemigrations` against a project where the
  migrations are hand-edited; record the desired state in the report
  and let the human reviewer run it.

## Forbidden

- New runtime dependency without explicit justification and a
  `dependency-change-review` pass.
- New test framework, assertion library, or mocking library.
- Linter / formatter / type-checker introduction (even "to improve
  quality") unless explicitly approved.
- `pip install`, `poetry add`, `uv add` unless strictly necessary
  and explicitly approved.
- Changes to `pyproject.toml` for implementation purposes unless
  explicitly approved.

## Async rules

- If the repo uses `async def` everywhere, use `async def` for new
  code. If it uses sync only, use sync.
- Do not mix sync and async DB calls in the same function.
- `pytest-asyncio` only if already configured.
