# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Async API wrapper for HoYoLAB/Miyoushe APIs (Genshin Impact, Honkai Impact 3rd, Honkai: Star Rail, Zenless Zone Zero). Python 3.9+, asyncio, pydantic v2, aiohttp. Managed with `uv` and `nox`.

> See also `AGENTS.md` (condensed agent guide) and `.roo/rules-code/AGENTS.md` (post-edit hook + coding rules). This file expands on the architecture.

## Commands

```bash
nox -s test                                       # run all tests
nox -s test -- tests/client/test_gacha.py         # single test file
nox -s test -- tests/client/test_gacha.py::test_wish_history  # single test
nox -s test -- -k "wish"                          # filter by keyword
nox -s lint                                        # ruff check
nox -s reformat                                    # black + ruff fix + sort __all__ (RUF022,I)
nox -s type-check                                  # pyright (strict) + mypy
nox -s verify-types                                # pyright --verifytypes (type completeness)
nox -s                                             # all default sessions
nox --no-install -s test                           # skip reinstalling deps (faster)
uv sync --all-groups --all-extras                  # install all dev deps
```

After editing any `.py` file, run `ruff check --fix <files> && ruff format <files>` (per `.roo/rules-code` post-edit hook).

## Architecture

**Client = mixin composition.** `genshin.Client` (`client/clients.py`) is assembled by multiply-inheriting one component class per API category from `client/components/` (e.g. `BattleChronicleClient`, `WishClient`, `AuthClient`). All components ultimately derive from `components/base.py`'s base client, which holds the cookie/session manager and the core request logic. To add an endpoint, add a method to the relevant component (or a new component, then add it to the `Client` bases). **Features are split by API endpoint in components.**

**Region split.** Almost every endpoint exists in two variants: OVERSEAS (HoYoLAB) and CHINESE (Miyoushe/米游社). This is handled by `InternationalRoute(overseas=..., chinese=...)` in `client/routes.py` — never hardcode URLs in components. The client's `region` (`types.Region`) selects which URL and which auth/header logic apply.

**Auth & cookies.** `client/manager/` parses cookies (`cookie.py`) and manages sessions + dynamic security headers like DS tokens (`managers.py`). The `auth/` component handles login flows (password, QR, mobile, game-login). Cookie-related optional deps (`browser-cookie3`, `rsa`, `qrcode`) live behind extras.

**Models, split by game then category.** `models/` has a base layer (`model.py`) plus per-game packages (`genshin/`, `starrail/`, `honkai/`, `zzz/`, `hoyolab/`, `auth/`). The API returns mixed Chinese/English fields; models rename them to clean English fields via aliases. Every model is a pydantic v2 `BaseModel`.

**Paginators** (`paginators/`) wrap cursor/page-based endpoints (e.g. wish/gacha history, transactions) as async iterables.

## Critical patterns (enforced)

- **Models** inherit from `APIModel` (`models/model.py`); use the `Unique` mixin for hashable models with an `id`.
- **Field aliases**: use `Aliased("api_field_name")` from `genshin.models.model`, NOT `pydantic.Field(alias=...)`. `Aliased` and constants are the only symbols imported directly (otherwise import whole modules).
- **Datetime fields**: annotate with `TZDateTime`, `DateTime`, or `UnixDateTime` from `model.py` — these are `Annotated` types with validators baked in, not functions to call.
- **Enums**: wrap unknown API enum values with `prevent_enum_error(value, EnumClass)` to avoid crashing on new game content.
- **Routes**: define endpoints as `Route(...)` / `InternationalRoute(...)` in `client/routes.py`.
- **`from __future__ import annotations`** must be the first import in every `.py` file (forward refs + 3.9 compat).
- **`__all__`** declared in every module; `nox -s reformat` auto-sorts it.
- **Python 3.9 typing**: use `typing.Optional[X]`, `typing.Union[X, Y]`, `typing.List`, `typing.Sequence` — NOT `X | Y` or `list[X]`. Import `typing` as a module and prefix (`typing.Optional`), prioritizing `typing` over `collections.abc`.
- **Docstrings** required for all exported symbols (numpy convention); `@property` exempt. Line length 120.
- pyright runs in **strict mode** over `genshin/` (excludes `**/__init__.py` and `tests/`).

## Testing

- Tests are **integration tests against live APIs** and require real account cookies via env vars: `GENSHIN_COOKIES`, `HSR_COOKIES`, `HONKAI_COOKIES`, `ZZZ_COOKIES`, `CHINESE_GENSHIN_COOKIES` (optional: `LOCAL_GENSHIN_COOKIES`, `GENSHIN_AUTHKEY`). Tests skip automatically when credentials are absent; model/unit tests run without them.
- `asyncio_mode = "auto"` — test functions are `async def` with no `@pytest.mark.asyncio`.
- A shared `client: genshin.Client` fixture is defined in `tests/conftest.py`; `ruff.toml` excludes `tests/` and `test.py` from linting.
