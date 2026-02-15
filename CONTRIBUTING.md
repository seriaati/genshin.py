# Genshin.py contributing guidelines

Contributions are always welcome and any amount of time spent on this project is greatly appreciated.

But before you get started contributing, it's recommended that you read through the following guide in-order to ensure that any pull-requests you open can be at their best from the start.

## Setting Up Your Development Environment

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/seriaati/genshin.py.git
   cd genshin.py
   ```

2. **Install uv (recommended)**

   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or with pip
   pip install uv
   ```

3. **Install Nox**

   ```bash
   pip install nox
   ```

4. **Install the package with all dependencies (optional)**

   ```bash
   uv sync --all-groups --all-extras
   ```

   This installs all development dependencies including testing, linting, and type-checking tools.

### Running Tests and Checks

The most important thing to consider while contributing towards Genshin.py is the checks the library's run against.
While these are run against all PRs by Github Actions, you can run these locally before any PR is opened using Nox.

#### Available Nox Tasks

Run `nox -l` to see all available tasks. The default tasks (run with `nox -s`) are:

- `reformat` - Auto-format code with black and ruff
- `lint` - Check code with ruff
- `type-check` - Run pyright and mypy type checkers
- `verify-types` - Verify type completeness
- `test` - Run pytest test suite

#### Common Commands

```bash
# Run all default checks (reformat, lint, type-check, verify-types, test)
nox -s

# Run specific tasks
nox -s test
nox -s lint
nox -s type-check
nox -s reformat

# Run multiple tasks at once
nox -s lint type-check test

# Skip reinstalling dependencies for faster runs
nox --no-install

# View verbose output
nox -v
```

### Tests

All changes contributed to this project should be tested. This repository uses pytest with `pytest-asyncio` for async test support.

#### Running Tests

```bash
# Run all tests
nox -s test

# Filter tests by keyword
nox -s test -- -k "wish"          # Only wish-related tests
nox -s test -- -k "genshin"       # Only Genshin Impact tests
nox -s test -- -k "chronicle"     # Only battle chronicle tests

# Run a specific test file
nox -s test -- tests/client/test_gacha.py

# Run a specific test function
nox -s test -- tests/client/test_gacha.py::test_wish_history

# Run with verbose output
nox -s test -- -v

# Run with coverage report
nox -s test -- --cov-report=html
```

#### Setting Up Test Credentials

Many tests require valid HoYoLAB/Miyoushe account cookies. Set these as environment variables:

```bash
# For overseas accounts
export GENSHIN_COOKIES="ltuid=123456; ltoken=abcdef..."
export HSR_COOKIES="ltuid=123456; ltoken=abcdef..."
export HONKAI_COOKIES="ltuid=123456; ltoken=abcdef..."
export ZZZ_COOKIES="ltuid=123456; ltoken=abcdef..."

# For Chinese accounts
export CHINESE_GENSHIN_COOKIES="ltuid=123456; ltoken=abcdef..."

# Optional: For local browser cookies
export LOCAL_GENSHIN_COOKIES="ltuid=123456; ltoken=abcdef..."
export GENSHIN_AUTHKEY="your_authkey_here"
```

**Note:** Tests will automatically skip if credentials are not provided. You can run model tests and other unit tests without any credentials.

### Type checking

All contributions to this project will have to be "type-complete" and, while [the nox tasks](###Available Nox Tasks) let you check that the type hints you've added/changed are type safe,
[pyright's type-completness guidelines](https://github.com/microsoft/pyright/blob/main/docs/typed-libraries.md) and
[standard typing library's type-completness guidelines](https://github.com/python/typing/blob/master/docs/libraries.md) are
good references for how projects should be type-hinted to be type-complete.

---

**NOTES**

- This project deviates from the common convention of importing types from the typing module and instead
  imports the typing module itself to use generics and types in it like `typing.Union` and `typing.Optional`.
- Since this project supports python 3.9+, the `typing` module takes priority over `collections.abc`.
- All exported symbols should have docstrings.

---

### General enforced style

- All modules should start with imports followed by declaration of `__all__`.
- [pep8](https://www.python.org/dev/peps/pep-0008/) should be followed as much as possible with notable cases where its ignored being that [black](https://github.com/psf/black) style may override this.
- The maximum character count for a line is 120 characters.
- Only entire modules may be imported with the exception of `Aliased` and constants.
- All public modules should be explicitly imported into its packages' `__init__.py` except for utilities and individual components which should only be exposed as an entire module.
- Features should be split by API endpoint in components and by game and category in models.
- Only abstract methods may be overwritten.

### Project structure

```plaintext
genshin
│
│   constants.py    = global constants like supported languages
│   errors.py       = all errors raised in the library
│   types.py        = enums required in some endpoint parameters
│
├───client          = client used for requests
│   │   clients.py      = final client composed from components
│   │   cache.py        = client cache implementations
│   │   compatibility.py = reverse-compatibility layer
│   │   ratelimit.py    = ratelimit handler
│   │   routes.py       = routes for various endpoints
│   │
│   ├───manager         = cookie and auth management
│   │       cookie.py       = cookie parsing utilities
│   │       managers.py     = cookie and session managers
│   │
│   └───components      = separate client components separated by category
│       │   base.py         = base client without any specific routes
│       │   auth/           = authentication components
│       │   calculator/     = calculator endpoints
│       │   chronicle/      = battle chronicle endpoints
│       └   ...             = other endpoint-specific components
│
├───paginators      = paginators used in the library
│
├───models          = models used in the library
│   │   model.py        = base model and helper fields
│   │
│   ├───genshin         = Genshin Impact specific models
│   ├───starrail        = Honkai: Star Rail specific models
│   ├───honkai          = Honkai Impact 3rd specific models
│   ├───zzz             = Zenless Zone Zero specific models
│   ├───hoyolab         = HoYoLAB community models
│   └───auth            = authentication models
│
└───utility         = utilities for the library
```
