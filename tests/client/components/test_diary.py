import datetime
import typing

import pytest

import genshin
from genshin.constants import CN_TIMEZONE


async def test_diary(lclient: genshin.Client, genshin_uid: int):
    diary = await lclient.get_genshin_diary()
    assert diary.uid == genshin_uid == lclient.uids[genshin.Game.GENSHIN]
    assert diary.month == datetime.datetime.now().month
    assert diary.data.current_mora >= 0
    assert diary.month in diary.optional_month


async def test_diary_log(lclient: genshin.Client, genshin_uid: int):
    log = lclient.genshin_diary_log(limit=10)
    data = await log.flatten()

    if data:
        assert data[0].amount > 0

    assert log.data.uid == genshin_uid == lclient.uids[genshin.Game.GENSHIN]
    assert log.data.month == datetime.datetime.now().month


async def test_starrail_diary(hsr_client: genshin.Client, hsr_uid: int):
    diary = await hsr_client.get_starrail_diary()
    assert diary.uid == hsr_uid
    assert str(diary.month) == datetime.datetime.now(CN_TIMEZONE).strftime("%Y%m")
    assert str(diary.month) in diary.optional_month
    assert diary.data.current_hcoin >= 0


async def test_starrail_diary_month(hsr_client: genshin.Client):
    month = (await hsr_client.get_starrail_diary()).optional_month[-1]
    diary = await hsr_client.get_starrail_diary(month=month)
    assert str(diary.month) == month


async def test_starrail_diary_log(hsr_client: genshin.Client, hsr_uid: int):
    log = hsr_client.starrail_diary_log(limit=10)
    data = await log.flatten()

    if data:
        assert data[0].amount != 0

    assert log.data.uid == hsr_uid


async def test_starrail_diary_refreshes_cookie_token(hsr_cookies: typing.Mapping[str, str], hsr_uid: int):
    if "stoken" not in hsr_cookies:
        pytest.skip("No stoken in HSR cookies")

    updates: list[typing.Mapping[str, str]] = []
    cookies = {**hsr_cookies, "cookie_token_v2": "invalid"}
    client = genshin.Client(cookies, game=genshin.Game.STARRAIL, uid=hsr_uid, on_cookie_update=updates.append)

    diary = await client.get_starrail_diary()
    assert diary.uid == hsr_uid
    assert updates
    assert updates[-1]["cookie_token_v2"] != "invalid"
