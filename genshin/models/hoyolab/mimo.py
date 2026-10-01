"""HoYoLAB Traveling Mimo models."""

import datetime
import enum
import typing

import pydantic

from genshin import types
from genshin.models.model import Aliased, APIModel, TZDateTime, UnixDateTime, prevent_enum_error

__all__ = (
    "MimoGame",
    "MimoLotteryInfo",
    "MimoLotteryResult",
    "MimoLotteryReward",
    "MimoPointOperation",
    "MimoPointRecord",
    "MimoPointType",
    "MimoShopItem",
    "MimoShopItemStatus",
    "MimoTask",
    "MimoTaskStatus",
    "MimoTaskType",
    "PartialMimoLotteryReward",
)


class MimoTaskStatus(enum.IntEnum):
    """Mimo task status."""

    FINISHED = 1
    ONGOING = 2
    CLAIMED = 3


class MimoTaskType(enum.IntEnum):
    """Mimo task type."""

    FINISHABLE = 1
    """e.g. Sunday Advanced Tutorial: What is the core Charge mechanic?"""
    VISIT = 2
    """e.g. Visit the 【Honkai: Star Rail】 Interest Group on the day"""
    COMMENT = 3
    """e.g. Participate in this week's creative interactions and leave your creations in the comments"""
    VIEW_TOPIC = 4
    """e.g. View the "Roaming Through the Realm of Saurians" topic"""
    GI_LOGIN = 5
    """e.g. Log into Genshin Impact today"""
    GI_GAME = 6
    """e.g. Claim rewards from Ley Line Blossoms 2 times"""
    GI_COMMUNITY = 101
    """e.g. Browse today's must-see highlights"""
    GI_VIDEO = 102
    """e.g. Watch today's highlights for 15s"""
    HSR_GAME = 8
    """e.g. Complete Divergent Universe or Simulated Universe 1 time"""
    TRAILER = 10
    """e.g. Myriad Celestia Trailer — "After the Sunset" | Honkai: Star Rail"""
    ZZZ_DAILY_LOGIN = 12
    """e.g. Log into Zenless Zone Zero today"""
    ZZZ_CONSECUTIVE_LOGIN = 13
    """e.g. Log into the game for 7 days"""
    ZZZ_GAME = 16
    """e.g. Reach 400 Engagement today"""


class MimoPointOperation(enum.IntEnum):
    """Mimo point record operation type."""

    INCOME = 1
    EXPENSE = 2


class MimoPointType(enum.IntEnum):
    """Mimo point record point type."""

    MISSION = 1
    PRIZE_DRAW = 2
    EXCHANGED = 4


class MimoShopItemStatus(enum.IntEnum):
    """Mimo shop item status."""

    EXCHANGEABLE = 1
    NOT_EXCHANGEABLE = 2
    LIMIT_REACHED = 3
    SOLD_OUT = 4


class MimoGame(APIModel):
    """Mimo game."""

    id: int = Aliased("game_id")
    version_id: int
    expire_point: bool
    point: int
    start_time: TZDateTime
    end_time: TZDateTime

    @property
    def game(self) -> typing.Union[typing.Literal["hoyolab"], types.Game, int]:
        if self.id == 5:
            return "hoyolab"
        if self.id == 6:
            return types.Game.STARRAIL
        if self.id == 8:
            return types.Game.ZZZ
        if self.id == 2:
            return types.Game.GENSHIN
        return self.id


class MimoTask(APIModel):
    """Mimo task."""

    id: int = Aliased("task_id")
    name: str = Aliased("task_name")
    time_type: int
    point: int
    progress: int
    total_progress: int

    status: MimoTaskStatus
    jump_url: str
    window_text: str
    type: typing.Union[int, MimoTaskType] = Aliased("task_type")
    af_url: str

    @pydantic.field_validator("type", mode="before")
    def __transform_task_type(cls, v: int) -> typing.Union[int, MimoTaskType]:
        return prevent_enum_error(v, MimoTaskType)


class MimoShopItem(APIModel):
    """Mimo shop item."""

    id: int = Aliased("award_id")
    status: MimoShopItemStatus
    icon: str
    name: str
    cost: int
    stock: int
    user_count: int
    next_refresh_time: datetime.timedelta
    expire_day: int


class MimoPointRecord(APIModel):
    """Mimo point record."""

    operation: MimoPointOperation = Aliased("operator_type")
    point_type: typing.Union[int, MimoPointType]
    point: int
    created_at: UnixDateTime = Aliased("create_time")
    description: str = Aliased("desc")
    code: str = Aliased("exchange_code")

    @pydantic.field_validator("point_type", mode="before")
    def __transform_point_type(cls, v: int) -> typing.Union[int, MimoPointType]:
        return prevent_enum_error(v, MimoPointType)


class PartialMimoLotteryReward(APIModel):
    """Partial mimo lottery reward."""

    type: int
    icon: str
    name: str


class MimoLotteryReward(PartialMimoLotteryReward):
    """Mimo lottery reward."""

    expire_day: int


class MimoLotteryInfo(APIModel):
    """Mimo lottery info."""

    current_point: int = Aliased("point")
    cost: int
    current_count: int = Aliased("count")
    limit_count: int
    rewards: typing.Sequence[MimoLotteryReward] = Aliased("award_list")


class MimoLotteryResult(APIModel):
    """Mimo lottery result."""

    reward: PartialMimoLotteryReward
    reward_id: int = Aliased("award_id")
    game_id: int
    src_type: int
    code: str = Aliased("exchange_code")

    @pydantic.model_validator(mode="before")
    def __nest_reward(cls, v: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        v["reward"] = {"type": v.pop("type"), "icon": v.pop("icon"), "name": v.pop("name")}
        return v
