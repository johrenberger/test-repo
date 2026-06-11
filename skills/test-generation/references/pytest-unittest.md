# Python — pytest / unittest profile

Used by `test-generation` when the repo is Python and the test framework
detected is pytest or unittest.

## Detection

- `pytest` in `pyproject.toml` `[tool.pytest.ini_options]` or
  `[project.optional-dependencies]` or `requirements.txt` → pytest
- `import unittest` in test files and no pytest → unittest
- `tox.ini` / `noxfile.py` presence (informational, not required)
- `conftest.py` presence → pytest fixture conventions apply

## Test layout

- `tests/` directory (most common) or co-located `test_<file>.py`
  next to `<file>.py`
- `pytest.ini` / `pyproject.toml` `[tool.pytest.ini_options]` for config
- `conftest.py` at the root or per-directory for shared fixtures

## Style rules

- **pytest** if present — use `def test_*` functions. Use
  `pytest.fixture` and `pytest.raises`. Do not switch to unittest.
- **unittest** if pytest is not present — use `class TestX(unittest.TestCase)`
  with `test_*` methods. Do not introduce pytest.
- **Assertion style:** pytest uses plain `assert`. unittest uses
  `self.assertEqual(...)`. Match the existing style.
- **Mocking:** `unittest.mock` is standard. If `pytest-mock` (the `mocker`
  fixture) is already used, prefer it. Do not introduce a new mocking
  library.
- **Parametrize:** pytest's `@pytest.mark.parametrize` if pytest is used.
- **Async:** `pytest-asyncio` only if already configured. Do not add it.

## Coverage checklist mapping

| Case | pytest idiom |
| --- | --- |
| happy path | `assert result == expected` |
| validation failure | `with pytest.raises(ValueError): fn(bad)` |
| auth failure | mock the auth dependency, expect the right exception |
| not-found | mock returns `None`, expect `NotFoundError` |
| conflict | similar to not-found with explicit conflict |
| persistence | `mock_db.add.assert_called_once_with(...)` |
| boundary | `@pytest.mark.parametrize("n,expected", [...])` |
| regression | `# Regression: <link or issue>` in a comment |

## Forbidden

- New test framework, assertion library, or mocking library.
- `ruff`, `mypy`, `pytest-cov`, `pytest-xdist`, `hypothesis`, etc. without
  explicit approval — even if they would be a "good idea."
- Changes to `pyproject.toml` or `requirements.txt` for test purposes
  unless explicitly approved.

## Example skeleton (pytest)

```python
import pytest
from myapp.orders import get_order, OrderNotFound

def test_get_order_returns_order_when_it_exists():
    order = get_order("123")
    assert order.id == "123"


@pytest.mark.parametrize("order_id,exc", [
    ("does-not-exist", OrderNotFound),
    ("", ValueError),
])
def test_get_order_raises(order_id, exc):
    with pytest.raises(exc):
        get_order(order_id)
```
