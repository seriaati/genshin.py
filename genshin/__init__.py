"""Modern API wrapper for Genshin Impact & Honkai Impact 3rd built on asyncio and pydantic.

Documentation: https://gh.seria.moe/genshin.py

Source Code: https://github.com/seriaati/genshin.py
"""

from . import models, utility
from .client import *
from .constants import *
from .errors import *
from .types import *

__version__ = "1.0.0"
