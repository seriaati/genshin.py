"""Starrail chronicle challenge."""

import typing

import pydantic

from genshin.models.model import Aliased, APIModel
from genshin.models.starrail.character import FloorCharacter

from .base import PartialTime

__all__ = (
    "APCShadowBoss",
    "APCShadowFloor",
    "APCShadowFloorNode",
    "APCShadowSeason",
    "AnomalyArbitration",
    "AnomalyBossInfo",
    "AnomalyBossRecord",
    "AnomalyMiniBossInfo",
    "AnomalyMiniBossRecord",
    "AnomalyPlayer",
    "AnomalyRecord",
    "AnomalySeason",
    "AnomalySummary",
    "ChallengeBuff",
    "FictionFloor",
    "FictionFloorNode",
    "FloorNode",
    "StarRailAPCShadow",
    "StarRailChallenge",
    "StarRailChallengeFloor",
    "StarRailChallengeSeason",
    "StarRailFloor",
    "StarRailPureFiction",
)


class FloorNode(APIModel):
    """Node for a memory of chaos floor."""

    challenge_time: PartialTime
    avatars: list[FloorCharacter]


class StarRailChallengeFloor(APIModel):
    """Base model for star rail challenge floors."""

    id: int = Aliased("maze_id")
    name: str
    star_num: int
    starward_star_num: int = Aliased("extra_star_num", default=0)

    is_quick_clear: bool = Aliased("is_fast")
    has_starward_mode: bool = Aliased("is_tierce", default=False)
    starward_extra_stars: int = Aliased("extra_star_num", default=0)

    @pydantic.computed_field  # type: ignore[prop-decorator]
    @property
    def stars(self) -> int:
        """Number of stars earned on the floor."""
        return self.star_num + self.starward_star_num


class StarRailFloor(StarRailChallengeFloor):
    """Floor in a memory of chaos challenge."""

    round_num: int
    is_chaos: bool
    node_1: typing.Optional[FloorNode] = Aliased(default=None)
    node_2: typing.Optional[FloorNode] = Aliased(default=None)
    node_3: typing.Optional[FloorNode] = Aliased(default=None)


class StarRailChallengeSeason(APIModel):
    """A season of a challenge."""

    id: int = Aliased("schedule_id")
    name: str = Aliased("name_mi18n")
    status: str
    begin_time: PartialTime
    end_time: PartialTime


class StarRailChallenge(APIModel):
    """Memory of chaos challenge in a season."""

    name: str
    season: int = Aliased("schedule_id")
    begin_time: typing.Optional[PartialTime]
    end_time: typing.Optional[PartialTime]

    total_stars: int = Aliased("star_num")
    starward_stars: int = Aliased("extra_star_num", default=0)
    max_floor: str
    max_floor_id: int
    total_battles: int = Aliased("battle_num")
    has_data: bool
    starward_star: int = Aliased("extra_star_num", default=0)

    floors: typing.Sequence[StarRailFloor] = Aliased("all_floor_detail")
    seasons: typing.Sequence[StarRailChallengeSeason] = Aliased("groups")

    @pydantic.model_validator(mode="before")
    def __extract_name(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "groups" in values and isinstance(values["groups"], list):
            seasons = typing.cast(list[dict[str, typing.Any]], values["groups"])
            if len(seasons) > 0:
                values["name"] = seasons[0]["name_mi18n"]
            else:
                values["name"] = ""

        return values


class ChallengeBuff(APIModel):
    """Buff used in a pure fiction or apocalyptic shadow node."""

    id: int
    name: str = Aliased("name_mi18n")
    description: str = Aliased("desc_mi18n")
    simple_description: typing.Optional[str] = Aliased("simple_desc_mi18m", default=None)  # only for PF
    icon: str


class FictionFloorNode(FloorNode):
    """Node for a Pure Fiction floor."""

    buff: typing.Optional[ChallengeBuff]
    score: int


class FictionFloor(StarRailChallengeFloor):
    """Floor in a Pure Fiction challenge."""

    round_num: int
    node_1: typing.Optional[FictionFloorNode] = Aliased(default=None)
    node_2: typing.Optional[FictionFloorNode] = Aliased(default=None)
    node_3: typing.Optional[FictionFloorNode] = Aliased(default=None)

    @property
    def score(self) -> int:
        """Total score of the floor."""
        node_1_score = self.node_1.score if self.node_1 is not None else 0
        node_2_score = self.node_2.score if self.node_2 is not None else 0
        node_3_score = self.node_3.score if self.node_3 is not None else 0
        return node_1_score + node_2_score + node_3_score


class StarRailPureFiction(APIModel):
    """Pure Fiction challenge in a season."""

    name: str = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")
    season_id: int = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")
    begin_time: PartialTime = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")
    end_time: PartialTime = pydantic.Field(deprecated="Use `season_id` together with `seasons instead`.")

    total_stars: int = Aliased("star_num")
    starward_stars: int = Aliased("extra_star_num", default=0)
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool
    starward_star: int = Aliased("extra_star_num", default=0)

    floors: list[FictionFloor] = Aliased("all_floor_detail")
    seasons: list[StarRailChallengeSeason] = Aliased("groups")
    max_floor_id: int

    @pydantic.model_validator(mode="before")
    def __unnest_groups(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "groups" in values and isinstance(values["groups"], list):
            seasons = typing.cast(list[dict[str, typing.Any]], values["groups"])
            if len(seasons) > 0:
                values["name"] = seasons[0]["name_mi18n"]
                values["season_id"] = seasons[0]["schedule_id"]
                values["begin_time"] = seasons[0]["begin_time"]
                values["end_time"] = seasons[0]["end_time"]

        return values


class APCShadowFloorNode(FloorNode):
    """Node for a apocalyptic shadow floor."""

    challenge_time: typing.Optional[PartialTime]  # type: ignore[assignment]
    buff: typing.Optional[ChallengeBuff]
    score: int
    boss_defeated: bool

    @property
    def has_data(self) -> bool:
        """Check if the node has data."""
        return bool(self.avatars)


class APCShadowFloor(StarRailChallengeFloor):
    """Floor in an apocalyptic shadow challenge."""

    node_1: typing.Optional[APCShadowFloorNode] = Aliased(default=None)
    node_2: typing.Optional[APCShadowFloorNode] = Aliased(default=None)
    node_3: typing.Optional[APCShadowFloorNode] = Aliased(default=None)
    last_update_time: PartialTime

    @property
    def score(self) -> int:
        """Total score of the floor."""
        node_1_score = self.node_1.score if self.node_1 is not None else 0
        node_2_score = self.node_2.score if self.node_2 is not None else 0
        node_3_score = self.node_3.score if self.node_3 is not None else 0
        return node_1_score + node_2_score + node_3_score


class APCShadowBoss(APIModel):
    """Boss in an apocalyptic shadow challenge."""

    id: int
    name: str = Aliased("name_mi18n")
    icon: str


class APCShadowSeason(StarRailChallengeSeason):
    """Season of an apocalyptic shadow challenge."""

    upper_boss: APCShadowBoss
    lower_boss: APCShadowBoss
    starward_boss: typing.Optional[APCShadowBoss] = Aliased("tierce_boss", default=None)


class StarRailAPCShadow(APIModel):
    """Apocalyptic shadow challenge in a season."""

    total_stars: int = Aliased("star_num")
    starward_stars: int = Aliased("extra_star_num", default=0)
    max_floor: str
    total_battles: int = Aliased("battle_num")
    has_data: bool

    floors: list[APCShadowFloor] = Aliased("all_floor_detail")
    seasons: list[APCShadowSeason] = Aliased("groups")
    max_floor_id: int


class AnomalySeason(APIModel):
    """Anomaly Arbitration season."""

    id: int = Aliased("group_id")
    begin_time: PartialTime
    end_time: PartialTime
    status: str
    name: str = Aliased("name_mi18n")
    game_version: str
    icon: str = Aliased("theme_pic_path")


class AnomalyBossInfo(APIModel):
    """Anomaly Arbitration boss info."""

    id: int = Aliased("maze_id")
    name: str = Aliased("name_mi18n")
    game_mode_name: str = Aliased("hard_mode_name_mi18n")
    icon: str


class AnomalyMiniBossInfo(APIModel):
    """Anomaly Arbitration mini boss info."""

    id: int = Aliased("maze_id")
    level_name: str = Aliased("name")
    name: str = Aliased("monster_name")
    icon: str = Aliased("monster_icon")


class AnomalyBossRecord(APIModel):
    """Anomaly Arbitration boss record."""

    id: int = Aliased("maze_id")
    has_data: bool = Aliased("has_challenge_record")
    time: PartialTime = Aliased("challenge_time")
    characters: list[FloorCharacter] = Aliased("avatars")
    buff: ChallengeBuff
    is_hard_mode: bool = Aliased("hard_mode")
    cycles_used: int = Aliased("round_num")
    stars: int = Aliased("star_num")
    has_color_medal: bool = Aliased("finish_color_medal")
    medal_type: str = Aliased("challenge_peak_rank_icon_type")
    medal_icon: str = Aliased("challenge_peak_rank_icon")
    record_unique_key: str


class AnomalyMiniBossRecord(APIModel):
    """Anomaly Arbitration mini boss record."""

    id: int = Aliased("maze_id")
    has_data: bool = Aliased("has_challenge_record")
    time: typing.Optional[PartialTime] = Aliased("challenge_time")
    characters: list[FloorCharacter] = Aliased("avatars")
    cycles_used: int = Aliased("round_num")
    stars: int = Aliased("star_num")
    is_quick_clear: bool = Aliased("is_fast")


class AnomalyRecord(APIModel):
    """HSR Anomaly Arbitration record."""

    season: AnomalySeason = Aliased("group")
    boss: AnomalyBossInfo = Aliased("boss_info")
    mini_bosses: list[AnomalyMiniBossInfo] = Aliased("mob_infos")
    has_data: bool = Aliased("has_challenge_record")
    cycles_used: int = Aliased("battle_num")

    boss_record: typing.Optional[AnomalyBossRecord] = Aliased("boss_record", default=None)
    mini_boss_records: list[AnomalyMiniBossRecord] = Aliased("mob_records")

    boss_stars: int
    mini_boss_stars: int = Aliased("mob_stars")


class AnomalySummary(APIModel):
    """HSR Anomaly Arbitration summary."""

    challenge_attempts: int = Aliased("total_battle_num")
    mini_boss_stars: int = Aliased("mob_stars")
    boss_stars: int
    medal_type: str = Aliased("challenge_peak_rank_icon_type")
    medal_icon: str = Aliased("challenge_peak_rank_icon")


class AnomalyPlayer(APIModel):
    """HSR Anomaly Arbitration player info."""

    server: str
    nickname: str
    level: int
    uid: str = Aliased("role_id")


class AnomalyArbitration(APIModel):
    """HSR Anomaly Arbitration info."""

    records: list[AnomalyRecord] = Aliased("challenge_peak_records")
    summary: typing.Optional[AnomalySummary] = Aliased("challenge_peak_best_record_brief", default=None)
    player: AnomalyPlayer = Aliased("role")
