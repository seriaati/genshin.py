"""Types used in the library."""

import enum
import typing

import typing_extensions

if typing.TYPE_CHECKING:
    from genshin.models.auth import SessionMMT, SessionMMTResult, SessionMMTv4, SessionMMTv4Result
    from genshin.models.model import Unique

__all__ = ["Game", "Region"]

UniqueT = typing.TypeVar("UniqueT", bound="Unique")


class Region(str, enum.Enum):
    """Region to get data from."""

    OVERSEAS = "os"
    """Applies to all overseas APIs."""

    CHINESE = "cn"
    """Applies to all chinese mainland APIs."""


class Game(str, enum.Enum):
    """Hoyoverse game."""

    GENSHIN = "genshin"
    """Genshin Impact"""

    HONKAI = "honkai3rd"
    """Honkai Impact 3rd"""

    STARRAIL = "hkrpg"
    """Honkai Star Rail"""

    ZZZ = "nap"
    """Zenless Zone Zero"""

    TOT = "tot"
    """Tears of Themis"""


IDOr: typing_extensions.TypeAlias = typing.Union[int, UniqueT]
"""Allows partial objects."""

Lang: typing_extensions.TypeAlias = typing.Literal[
    "zh-cn",
    "zh-tw",
    "de-de",
    "en-us",
    "es-es",
    "fr-fr",
    "id-id",
    "it-it",
    "ja-jp",
    "ko-kr",
    "pt-pt",
    "ru-ru",
    "th-th",
    "vi-vn",
    "tr-tr",
]

AppGeetestSession: typing_extensions.TypeAlias = typing.Union[
    "SessionMMT",
    "SessionMMTv4",
]
"""Geetest session returned by the API."""

AppGeetestResult: typing_extensions.TypeAlias = typing.Union[
    "SessionMMTResult",
    "SessionMMTv4Result",
]
"""Solved geetest result."""

AppGeetestSolver: typing_extensions.TypeAlias = typing.Callable[
    [AppGeetestSession],
    typing.Awaitable[AppGeetestResult],
]
"""Asynchronous geetest solver callable."""
