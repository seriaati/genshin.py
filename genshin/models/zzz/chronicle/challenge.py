import datetime
import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, DateTime, TZDateTime
from genshin.models.starrail.chronicle.base import PartialTime
from genshin.models.zzz.character import ZZZElementType, ZZZSpecialty

__all__ = (
    "ChallengeBangboo",
    "DeadlyAssault",
    "DeadlyAssaultAgent",
    "DeadlyAssaultBoss",
    "DeadlyAssaultBuff",
    "DeadlyAssaultChallenge",
    "ShiyuDefense",
    "ShiyuDefenseBangboo",
    "ShiyuDefenseBuff",
    "ShiyuDefenseCharacter",
    "ShiyuDefenseFloor",
    "ShiyuDefenseMonster",
    "ShiyuDefenseNode",
    "ShiyuDefenseV1",
    "ShiyuDefenseV2",
    "ShiyuMonsterElementEffect",
    "ShiyuMonsterElementEffects",
    "ShiyuV2FifthFloor",
    "ShiyuV2FifthFloorLayer",
    "ShiyuV2FourthFloor",
    "ShiyuV2FourthFloorLayer",
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


class ShiyuMonsterElementEffect(enum.IntEnum):
    """Shiyu Defense monster element effect enum."""

    WEAKNESS = 1
    RESISTANCE = -1
    NEUTRAL = 0


class ShiyuDefenseBangboo(APIModel):
    """Shiyu Defense bangboo model."""

    id: int
    rarity: typing.Literal["S", "A"]
    level: int
    icon: str = Aliased("bangboo_rectangle_url")


class ChallengeBangboo(ShiyuDefenseBangboo):
    """Bangboo model for backward compatibility."""


class ShiyuDefenseCharacter(APIModel):
    """Shiyu Defense character model."""

    id: int
    level: int
    rarity: typing.Literal["S", "A"]
    element: ZZZElementType = Aliased("element_type")
    icon: str = Aliased("role_square_url")
    mindscape: int = Aliased("rank")


class ShiyuDefenseBuff(APIModel):
    """Shiyu Defense buff model."""

    name: str = Aliased("title")
    description: str = Aliased("text")


class ShiyuMonsterElementEffects(pydantic.BaseModel):
    """Shiyu Defense monster element effects model."""

    ice: ShiyuMonsterElementEffect = Aliased("ice_weakness")
    fire: ShiyuMonsterElementEffect = Aliased("fire_weakness")
    electric: ShiyuMonsterElementEffect = Aliased("elec_weakness")
    ether: ShiyuMonsterElementEffect = Aliased("ether_weakness")
    physical: ShiyuMonsterElementEffect = Aliased("physics_weakness")


class ShiyuDefenseMonster(APIModel):
    """Shiyu Defense monster model."""

    id: int
    name: str
    weakness: typing.Union[ZZZElementType, int] = Aliased(
        "weak_element_type", deprecated="ShiyuDefenseMonster.weakness doesn't return anything meaningful anymore."
    )
    level: int
    element_effects: ShiyuMonsterElementEffects

    @pydantic.model_validator(mode="before")
    @classmethod
    def __nest_element_effects(cls, v: dict[str, typing.Any]) -> dict[str, typing.Any]:
        v["element_effects"] = {
            "ice_weakness": v["ice_weakness"],
            "fire_weakness": v["fire_weakness"],
            "elec_weakness": v["elec_weakness"],
            "ether_weakness": v["ether_weakness"],
            "physics_weakness": v["physics_weakness"],
        }
        return v


class ShiyuDefenseNode(APIModel):
    """Shiyu Defense node model."""

    characters: list[ShiyuDefenseCharacter] = Aliased("avatars")
    bangboo: typing.Optional[ShiyuDefenseBangboo] = Aliased("buddy", default=None)
    recommended_elements: list[ZZZElementType] = Aliased("element_type_list")
    enemies: list[ShiyuDefenseMonster] = Aliased("monster_info")
    battle_time: typing.Optional[datetime.timedelta] = None

    @pydantic.field_validator("enemies", mode="before")
    @classmethod
    def __convert_enemies(cls, value: dict[typing.Literal["level", "list"], typing.Any]) -> list[ShiyuDefenseMonster]:
        level = value["level"]
        result: list[ShiyuDefenseMonster] = []
        for monster in value["list"]:
            monster["level"] = level
            result.append(ShiyuDefenseMonster(**monster))
        return result


class ShiyuDefenseFloor(APIModel):
    """Shiyu Defense floor model."""

    index: int = Aliased("layer_index")
    rating: typing.Literal["S", "A", "B"]
    id: int = Aliased("layer_id")
    buffs: list[ShiyuDefenseBuff]
    node_1: ShiyuDefenseNode
    node_2: ShiyuDefenseNode
    challenge_time: TZDateTime = Aliased("floor_challenge_time")
    name: str = Aliased("zone_name")

    @pydantic.field_validator("challenge_time", mode="before")
    @classmethod
    def __parse_datetime(cls, value: typing.Mapping[str, typing.Any]) -> typing.Optional[TZDateTime]:
        if value:
            return datetime.datetime(**value)
        return None


class ShiyuDefenseV1(APIModel):
    """ZZZ Shiyu Defense V1 model."""

    schedule_id: int
    begin_time: typing.Optional[DateTime] = Aliased("hadal_begin_time")
    end_time: typing.Optional[DateTime] = Aliased("hadal_end_time")
    has_data: bool
    ratings: typing.Mapping[typing.Literal["S", "A", "B"], int] = Aliased("rating_list")
    floors: list[ShiyuDefenseFloor] = Aliased("all_floor_detail")
    fastest_clear_time: int = Aliased("fast_layer_time")
    """Fastest clear time this season in seconds."""
    max_floor: int = Aliased("max_layer")

    @pydantic.field_validator("ratings", mode="before")
    @classmethod
    def __convert_ratings(
        cls, v: list[dict[typing.Literal["times", "rating"], typing.Any]]
    ) -> typing.Mapping[typing.Literal["S", "A", "B"], int]:
        return {d["rating"]: d["times"] for d in v}

    @pydantic.computed_field  # type: ignore[prop-decorator]
    @property
    def total_clear_time(self) -> int:
        """Total clear time for all floors in seconds."""
        total = 0
        for floor in self.floors:
            for node in (floor.node_1, floor.node_2):
                if node.battle_time is None:
                    continue
                total += int(node.battle_time.total_seconds())
        return total


ShiyuDefense = ShiyuDefenseV1  # Backward compatibility


class ShiyuV2FifthFloorLayer(APIModel):
    """ZZZ Shiyu Defense V2 fifth floor layer model."""

    id: int = Aliased("layer_id")
    rating: typing.Literal["S", "A", "B"]
    buff: ShiyuDefenseBuff = Aliased("buffer")
    score: int
    max_score: int
    clear_time: int = Aliased("battle_time")
    """Clear time in seconds."""
    boss_icon: str = Aliased("monster_pic")
    bangboo: typing.Optional[ShiyuDefenseBangboo] = Aliased("buddy", default=None)
    characters: typing.Sequence[ShiyuDefenseCharacter] = Aliased("avatar_list")


class ShiyuV2FifthFloor(APIModel):
    """ZZZ Shiyu Defense V2 fifth floor model."""

    layers: typing.Sequence[ShiyuV2FifthFloorLayer] = Aliased("layer_challenge_info_list")


class ShiyuV2FourthFloorLayer(APIModel):
    """ZZZ Shiyu Defense V2 fourth floor layer model."""

    id: int = Aliased("layer_id")
    clear_time: int = Aliased("battle_time")
    """Clear time in seconds."""
    characters: typing.Sequence[ShiyuDefenseCharacter] = Aliased("avatar_list")
    bangboo: typing.Optional[ShiyuDefenseBangboo] = Aliased("buddy", default=None)


class ShiyuV2FourthFloor(APIModel):
    """ZZZ Shiyu Defense V2 fourth floor model."""

    buff: ShiyuDefenseBuff = Aliased("buffer")
    challenge_time: DateTime
    rating: typing.Literal["S", "A", "B"]
    layers: typing.Sequence[ShiyuV2FourthFloorLayer] = Aliased("layer_challenge_info_list")


class ShiyuV2BriefInfo(APIModel):
    """ZZZ Shiyu Defense V2 brief info."""

    score: int
    max_score: int
    rank_percent: str
    total_clear_time: int = Aliased("battle_time")
    rating: typing.Literal["S+", "S", "A", "B"]
    challenge_time: DateTime

    @pydantic.field_validator("rank_percent", mode="before")
    def __parse_rank_percent(cls, value: int) -> str:
        return f"{value / 100}%"


class ShiyuDefenseV2(APIModel):
    """ZZZ Shiyu Defense V2 model."""

    schedule_id: int = Aliased("zone_id")
    begin_time: typing.Optional[DateTime] = Aliased("hadal_begin_time")
    end_time: typing.Optional[DateTime] = Aliased("hadal_end_time")
    passed_fifth_floor: bool = Aliased("pass_fifth_floor")

    brief_info: ShiyuV2BriefInfo = Aliased("brief")
    fourth_frontier: ShiyuV2FourthFloor = Aliased("fourth_layer_detail")
    fifth_frontier: ShiyuV2FifthFloor = Aliased("fitfh_layer_detail")  # Nice typo hoyo

    player_nickname: str = Aliased("nick_name")
    player_avatar: str = Aliased("icon")


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
    bangboo: typing.Optional[ShiyuDefenseBangboo] = Aliased("buddy", default=None)

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
