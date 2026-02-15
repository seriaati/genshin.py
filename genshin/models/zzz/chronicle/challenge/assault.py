import datetime
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, DateTime, TZDateTime
from genshin.models.zzz.character import ZZZElementType, ZZZSpecialty

from .common import ChallengeBangboo

__all__ = (
    "DeadlyAssault",
    "DeadlyAssaultAgent",
    "DeadlyAssaultBoss",
    "DeadlyAssaultBuff",
    "DeadlyAssaultChallenge",
)


class DeadlyAssaultBoss(APIModel):
    """ZZZ Deadly Assault boss."""

    icon: str
    name: str
    background: str = Aliased("bg_icon")
    badge_icon: str = Aliased("race_icon")


class DeadlyAssaultBuff(APIModel):
    """ZZZ Deadly Assault buff model."""

    name: str
    description: str = Aliased("desc")
    icon: str


class DeadlyAssaultAgent(APIModel):
    """ZZZ Deadly Assault agent model."""

    id: int
    level: int
    element: ZZZElementType = Aliased("element_type")
    specialty: ZZZSpecialty = Aliased("avatar_profession")
    rarity: typing.Literal["S", "A"]
    mindscape: int = Aliased("rank")
    icon: str = Aliased("role_square_url")


class DeadlyAssaultChallenge(APIModel):
    """ZZZ Deadly Assault challenge model."""

    score: int
    star: int
    total_star: int
    challenge_time: datetime.datetime

    boss: DeadlyAssaultBoss
    buffs: typing.Sequence[DeadlyAssaultBuff] = Aliased("buffer")
    agents: typing.Sequence[DeadlyAssaultAgent] = Aliased("avatar_list")
    bangboo: typing.Optional[ChallengeBangboo] = Aliased("buddy", default=None)

    @pydantic.field_validator("challenge_time", mode="before")
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> typing.Optional[TZDateTime]:
        if value:
            return datetime.datetime(**value)
        return None

    @pydantic.field_validator("boss", mode="before")
    def __parse_boss(cls, value: typing.List[typing.Mapping[str, typing.Any]]) -> DeadlyAssaultBoss:
        if not value:
            raise ValueError("No boss data provided.")
        return DeadlyAssaultBoss(**value[0])


class DeadlyAssault(APIModel):
    """ZZZ Deadly Assault model."""

    id: int = Aliased("zone_id")
    start_time: typing.Optional[DateTime]
    end_time: typing.Optional[DateTime]

    challenges: typing.Sequence[DeadlyAssaultChallenge] = Aliased("list")
    has_data: bool
    total_score: int
    total_star: int
    rank_percent: str

    nickname: str = Aliased("nick_name")
    player_avatar: str = Aliased("avatar_icon")

    @pydantic.field_validator("rank_percent", mode="before")
    def __parse_rank_percent(cls, value: int) -> str:
        return f"{value / 100}%"
