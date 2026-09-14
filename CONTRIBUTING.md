# Contributing

## Development flow
1. Fork and create a feature branch.
2. Install dependencies: `pip install -r requirements.txt`
3. Run checks before PR:
   - `ruff check .`
   - `black --check .`
   - `pytest`
4. Open PR with clear description and tests.

## Commit style
Use conventional commits, for example:
- feat: add booking conflict protection
- fix: enforce tenant scoped queryset
- test: add invitation expiration tests

## Code standards
- Avoid hardcoded secrets.
- Keep tenant isolation in every query.
- Add tests for critical business logic.
