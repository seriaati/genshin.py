"""Constants hardcoded for optimizations."""

import datetime
import typing

from . import types

__all__ = [
    "APP_IDS",
    "APP_KEYS",
    "CN_TIMEZONE",
    "DS_SALT",
    "GAME_BIZS",
    "GAME_LANGS",
    "GEETEST_RECORD_KEYS",
    "GEETEST_RETCODES",
    "LANGS",
]


LANGS: typing.Final[typing.Dict[types.Lang, str]] = {
    "zh-cn": "简体中文",
    "zh-tw": "繁體中文",
    "de-de": "Deutsch",
    "en-us": "English",
    "es-es": "Español",
    "fr-fr": "Français",
    "id-id": "Indonesia",
    "it-it": "Italiano",
    "ja-jp": "日本語",
    "ko-kr": "한국어",
    "pt-pt": "Português",
    "ru-ru": "Pусский",
    "th-th": "ภาษาไทย",
    "vi-vn": "Tiếng Việt",
    "tr-tr": "Türkçe",
}
"""Languages supported by the API."""

# https://webstatic.hoyoverse.com/admin/mi18n/plat_cn/m10201340231541/m10201340231541-zh-cn.json
GAME_LANGS: typing.Final[typing.Dict[types.Game, typing.Tuple[types.Lang, ...]]] = {
    types.Game.HONKAI: (
        "zh-cn",
        "zh-tw",
        "de-de",
        "en-us",
        "es-es",
        "fr-fr",
        "id-id",
        "ja-jp",
        "ko-kr",
        "pt-pt",
        "ru-ru",
        "th-th",
        "vi-vn",
    ),
    types.Game.GENSHIN: (
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
        "tr-tr",
        "vi-vn",
    ),
    types.Game.STARRAIL: (
        "zh-cn",
        "zh-tw",
        "de-de",
        "en-us",
        "es-es",
        "fr-fr",
        "id-id",
        "ja-jp",
        "ko-kr",
        "pt-pt",
        "ru-ru",
        "th-th",
        "vi-vn",
    ),
    types.Game.ZZZ: (
        "zh-cn",
        "zh-tw",
        "de-de",
        "en-us",
        "es-es",
        "fr-fr",
        "id-id",
        "ja-jp",
        "ko-kr",
        "pt-pt",
        "ru-ru",
        "th-th",
        "vi-vn",
    ),
    types.Game.TOT: (
        "zh-cn",
        "zh-tw",
        "de-de",
        "en-us",
        "es-es",
        "fr-fr",
        "id-id",
        "ja-jp",
        "ko-kr",
        "pt-pt",
        "ru-ru",
        "th-th",
        "vi-vn",
    ),
}

DS_SALT: typing.Final[typing.Dict[typing.Union[types.Region, str], str]] = {
    types.Region.OVERSEAS: "6s25p5ox5y14umn1p61aqyyvbvvl3lrt",
    types.Region.CHINESE: "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs",
    "app_login": "IZPgfb0dRPtBeLuFkdDznSZ6f4wWt6y2",
    "cn_signin": "LyD1rXqMv2GJhnwdvCBjFOKGiKuLY3aO",
    "cn_passport": "JwYDpKvLj6MrMqqYU6jTKF17KNO2PXoS",
}
"""Dynamic Secret Salts."""

GEETEST_RETCODES = {10035, 5003, 10041, 1034}
"""API error codes that indicate a Geetest was triggered during the API request."""

APP_KEYS = {
    types.Game.GENSHIN: {
        types.Region.OVERSEAS: "6a4c78fe0356ba4673b8071127b28123",
        types.Region.CHINESE: "d0d3a7342df2026a70f650b907800111",
    },
    types.Game.STARRAIL: {
        types.Region.OVERSEAS: "d74818dabd4182d4fbac7f8df1622648",
        types.Region.CHINESE: "4650f3a396d34d576c3d65df26415394",
    },
    types.Game.HONKAI: {
        types.Region.OVERSEAS: "243187699ab762b682a2a2e50ba02285",
        types.Region.CHINESE: "0ebc517adb1b62c6b408df153331f9aa",
    },
    types.Game.ZZZ: {
        types.Region.OVERSEAS: "ff0f2776bf515d79d1f8ff1fb98b2a06",
        types.Region.CHINESE: "4650f3a396d34d576c3d65df26415394",
    },
}
"""App keys used for game login."""

APP_IDS = {
    types.Game.GENSHIN: {
        types.Region.OVERSEAS: "4",
        types.Region.CHINESE: "4",
    },
    types.Game.STARRAIL: {
        types.Region.OVERSEAS: "11",
        types.Region.CHINESE: "8",
    },
    types.Game.HONKAI: {
        types.Region.OVERSEAS: "8",
        types.Region.CHINESE: "1",
    },
    types.Game.ZZZ: {
        types.Region.OVERSEAS: "15",
        types.Region.CHINESE: "12",
    },
}
"""App IDs used for game login."""

GEETEST_RECORD_KEYS = {
    types.Game.GENSHIN: "genshin_game_record",
    types.Game.STARRAIL: "hkrpg_game_record",
    types.Game.HONKAI: "bh3_game_record",
    types.Game.ZZZ: "nap_game_record",
    types.Game.TOT: "nxx_game_record",
}
"""Keys used to submit geetest result."""

CN_TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))

GAME_BIZS = {
    types.Region.OVERSEAS: {
        types.Game.GENSHIN: "hk4e_global",
        types.Game.STARRAIL: "hkrpg_global",
        types.Game.HONKAI: "bh3_os",
        types.Game.ZZZ: "nap_global",
    },
    types.Region.CHINESE: {
        types.Game.GENSHIN: "hk4e_cn",
        types.Game.STARRAIL: "hkrpg_cn",
        types.Game.HONKAI: "bh3_cn",
        types.Game.ZZZ: "nap_cn",
    },
}

WEB_EVENT_GAME_IDS = {
    types.Game.GENSHIN: 2,
    types.Game.STARRAIL: 6,
    types.Game.HONKAI: 1,
    types.Game.ZZZ: 8,
    types.Game.TOT: 4,
}

# Server names are from uid.py
SERVER_TIMEZONE_OFFSETS: typing.Final[dict[int, typing.Tuple[str, ...]]] = {
    8: (
        "cn_gf01",
        "cn_qd01",
        "os_asia",
        "os_cht",
        "prod_gf_cn",
        "prod_qd_cn",
        "prod_official_asia",
        "prod_official_cht",
        "prod_gf_sg",
        "prod_gf_jp",
        "prod_gf_cn",
    ),
    -5: ("os_usa", "prod_official_usa", "prod_gf_us"),
    1: ("os_euro", "prod_official_eur", "prod_gf_eu"),
}

CODE_SUPPORTED_GAMES = {types.Game.GENSHIN, types.Game.ZZZ, types.Game.STARRAIL, types.Game.TOT}
"""Games that support redeeming codes."""
