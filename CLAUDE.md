# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

genshin.py is an async API wrapper for HoYoLAB and Miyoushe (米游社) APIs, supporting multiple HoYoverse games (Genshin Impact, Honkai Impact, Star Rail, ZZZ). Built on asyncio and pydantic with full type-hinting support.

## Development Commands

### Setup

```bash
pip install nox
```

### Testing

```bash
# Run all default tasks (reformat, lint, type-check, verify-types, test)
nox -s

# Run specific tasks
nox -s test
nox -s lint
nox -s type-check
nox -s reformat

# List all available tasks
nox -l

# Run tests without reinstalling dependencies
nox --no-install

# Filter tests by keyword
nox -s test -- -k "wish"
nox -s test -- -k "genshin"
```

### Single Test Execution

```bash
nox -s test -- tests/client/test_specific.py::test_function_name
```

### Type Checking

```bash
nox -s type-check      # Run pyright and mypy
nox -s verify-types    # Verify type completeness
```

### Linting and Formatting

```bash
nox -s reformat  # Auto-fix with black and ruff
nox -s lint      # Check with ruff
```

### Documentation

```bash
nox -s docs  # Generate pdoc3 documentation
```

## Architecture

### Client Architecture

The main `Client` class is composed through multiple inheritance of component classes, each handling specific API endpoints:

- **Base**: `BaseClient` in [components/base.py](genshin/client/components/base.py) - Core HTTP request handling, cookie management, auth, region/language settings
- **Components** in [client/components/](genshin/client/components/):
  - `BattleChronicleClient` - Game statistics and records
  - `HoyolabClient` - Community features (posts, users)
  - `DailyRewardClient` - Daily check-in rewards
  - `CalculatorClient` - Character/weapon calculations
  - `DiaryClient` - In-game currency transactions
  - `LineupClient` / `HSRLineupClient` - Team composition
  - `TeapotClient` - Genshin teapot/realm features
  - `WikiClient` - Game encyclopedia data
  - `WishClient` - Gacha/wish history
  - `TransactionClient` - Transaction logs
  - `AuthClient` - Authentication flows

### Models Architecture

Models in [genshin/models/](genshin/models/) are organized by game and feature category:

- **Base**: `APIModel` (Pydantic base class) in [model.py](genshin/models/model.py)
- **Game-specific directories**:
  - `genshin/` - Genshin Impact models
  - `starrail/` - Honkai: Star Rail models
  - `honkai/` - Honkai Impact models
  - `zzz/` - Zenless Zone Zero models
  - `hoyolab/` - HoYoLAB community models
  - `auth/` - Authentication models

All models inherit from `APIModel` and use Pydantic v2 for validation.

### Routes

API endpoints are defined in [client/routes.py](genshin/client/routes.py) using `Route` and `InternationalRoute` classes to handle region-specific URLs (OVERSEAS vs CHINESE regions).

### Cookie & Auth Management

Cookie handling in [client/manager/](genshin/client/manager/) supports multiple authentication methods and cookie formats. The `BaseCookieManager` handles cookie parsing and storage.

## Code Style & Conventions

### Import Style

- Import entire modules rather than individual symbols (exceptions: `Aliased` and constants)
- Use `typing.Optional` and `typing.Union` instead of `|` syntax (Python 3.9 compatibility)
- Import `typing` module itself, not individual types

### Module Structure

- All modules start with imports followed by `__all__` declaration
- Public modules must be explicitly imported in package `__init__.py`
- Only abstract methods may be overridden

### Type Hinting

- All code must be type-complete per pyright standards
- Functions must have full type annotations
- Use `typing.` prefix for generics (e.g., `typing.Optional`, `typing.List`)

### Formatting

- Line length: 120 characters (black/ruff enforced)
- Follow PEP 8 with black overrides
- Docstrings required for all exported symbols (numpy convention)

### Project-Specific Patterns

- Use `Aliased()` for pydantic field aliases mapping API field names to Pythonic names
- Models should inherit from `APIModel`
- Use `Unique` mixin for hashable models with IDs
- Custom datetime types: `TZDateTime`, `DateTime`, `UnixDateTime`

## Testing

Tests are in [tests/](tests/) mirroring the package structure. Test configuration uses environment variables for cookies:

- `GENSHIN_COOKIES` - Genshin Impact account cookies
- `HSR_COOKIES` - Star Rail account cookies
- `HONKAI_COOKIES` - Honkai Impact account cookies
- `ZZZ_COOKIES` - ZZZ account cookies
- `CHINESE_GENSHIN_COOKIES` - Chinese region cookies

See [conftest.py](tests/conftest.py) for fixture definitions. Tests use `pytest` with `pytest-asyncio` for async support.

## Important Files

- [pyproject.toml](pyproject.toml) - Project metadata, dependencies, tool configuration
- [noxfile.py](noxfile.py) - Task automation (testing, linting, type-checking)
- [ruff.toml](ruff.toml) - Linting rules and exclusions
- [CONTRIBUTING.md](CONTRIBUTING.md) - Detailed contribution guidelines and project structure
