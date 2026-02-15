import datetime
import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, DateTime, TZDateTime
from genshin.models.zzz.character import ZZZElementType

from .common import ChallengeBangboo

__all__ = (
    "ChallengeBangboo",
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
)


class ShiyuMonsterElementEffect(enum.IntEnum):
    """Shiyu Defense monster element effect enum."""

    WEAKNESS = 1
    RESISTANCE = -1
    NEUTRAL = 0


class ShiyuDefenseBangboo(ChallengeBangboo):
    """Shiyu Defense bangboo model."""


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
    rating: typing.Optional[typing.Literal["S+", "S", "A", "B"]]
    challenge_time: typing.Optional[DateTime] = None

    @pydantic.field_validator("rating", mode="before")
    def __parse_rating(
        cls, value: typing.Literal["S+", "S", "A", "B", ""]
    ) -> typing.Optional[typing.Literal["S+", "S", "A", "B"]]:
        return value or None

    @pydantic.field_validator("rank_percent", mode="before")
    def __parse_rank_percent(cls, value: int) -> str:
        return f"{value / 100}%"


class ShiyuDefenseV2(APIModel):
    """ZZZ Shiyu Defense V2 model."""

    schedule_id: int = Aliased("zone_id")
    begin_time: typing.Optional[DateTime] = Aliased("hadal_begin_time")
    end_time: typing.Optional[DateTime] = Aliased("hadal_end_time")
    passed_fifth_floor: bool = Aliased("pass_fifth_floor")

    brief_info: typing.Optional[ShiyuV2BriefInfo] = Aliased("brief", default=None)
    fourth_frontier: typing.Optional[ShiyuV2FourthFloor] = Aliased("fourth_layer_detail", default=None)
    fifth_frontier: typing.Optional[ShiyuV2FifthFloor] = Aliased("fitfh_layer_detail", default=None)  # Nice typo hoyo

    player_nickname: str = Aliased("nick_name")
    player_avatar: str = Aliased("icon")
