import typing

import pydantic

from genshin.models.model import Aliased, APIModel
from genshin.models.starrail.chronicle.base import PartialTime
from genshin.models.zzz.character import ZZZElementType

__all__ = (
    "ThresholdSimulation",
    "ThresholdSimulationBangboo",
    "ThresholdSimulationBoss",
    "ThresholdSimulationBossChallenge",
    "ThresholdSimulationBuff",
    "ThresholdSimulationChallenge",
    "ThresholdSimulationCharacter",
    "ThresholdSimulationInfo",
    "ThresholdSimulationMainChallenge",
    "ThresholdSimulationPlayer",
)


class ThresholdSimulationInfo(APIModel):
    """ZZZ Threshold Simulation brief info."""

    id: int = Aliased("void_front_id")
    time_remaining_over_42_days: bool = Aliased("end_ts_over_42_days")
    time_remaining_days: int = Aliased("end_ts")
    has_data: bool = Aliased("has_ending_record")
    ending_name: str = Aliased("ending_record_name")
    ending_background: str = Aliased("ending_record_bg_pic")
    total_score: int
    rank_percent: str

    @pydantic.field_validator("rank_percent", mode="before")
    def __parse_rank_percent(cls, value: int) -> str:
        return f"{value / 100}%"


class ThresholdSimulationCharacter(APIModel):
    """ZZZ Threshold Simulation character model."""

    id: int
    level: int
    element: ZZZElementType = Aliased("element_type")
    rarity: typing.Literal["S", "A"]
    mindscape: int = Aliased("rank")
    icon: str = Aliased("role_square_url")


class ThresholdSimulationBangboo(APIModel):
    """ZZZ Threshold Simulation bangboo model."""

    id: int
    rarity: typing.Literal["S", "A"]
    level: int
    icon: str = Aliased("bangboo_rectangle_url")


class ThresholdSimulationBoss(APIModel):
    """ZZZ Threshold Simulation boss model."""

    icon: str
    name: str
    badge_icon: str = Aliased("race_icon")
    background: str = Aliased("bg_icon")


class ThresholdSimulationBuff(APIModel):
    """ZZZ Threshold Simulation buff model."""

    name: str
    description: str = Aliased("desc")
    icon: str


class ThresholdSimulationChallenge(APIModel):
    """ZZZ Threshold Simulation challenge model."""

    id: int = Aliased("battle_id")
    name: str
    rating: typing.Literal["S", "A", "B"] = Aliased("star")

    characters: typing.Sequence[ThresholdSimulationCharacter] = Aliased("avatar_list")
    bangboo: typing.Optional[ThresholdSimulationBangboo] = Aliased("buddy", default=None)
    buff: ThresholdSimulationBuff = Aliased("buffer")


class ThresholdSimulationMainChallenge(ThresholdSimulationChallenge):
    """ZZZ Threshold Simulation main challenge model."""

    node_id: int
    score: int
    max_score: int
    score_multiplier: str = Aliased("score_ratio")
    time: PartialTime = Aliased("challenge_time")

    sub_challenges: typing.Sequence["ThresholdSimulationChallenge"] = Aliased("sub_challenge_record")


class ThresholdSimulationBossChallenge(APIModel):
    """ZZZ Threshold Simulation boss challenge model."""

    boss: ThresholdSimulationBoss = Aliased("boss_info")
    challenge: ThresholdSimulationMainChallenge = Aliased("main_challenge_record")


class ThresholdSimulationPlayer(APIModel):
    """ZZZ Threshold Simulation player info."""

    nickname: str
    server: str
    icon: str


class ThresholdSimulation(APIModel):
    """ZZZ Threshold Simulation."""

    info: ThresholdSimulationInfo = Aliased("void_front_battle_abstract_info_brief")
    boss_challenge: ThresholdSimulationBossChallenge = Aliased("boss_challenge_record")
    challenges: typing.Sequence[ThresholdSimulationChallenge] = Aliased("main_challenge_record_list")
    player: ThresholdSimulationPlayer = Aliased("role_basic_info")
