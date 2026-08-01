"""ZZZ agent upgrade guide models."""

from __future__ import annotations

import typing

import pydantic

from genshin.models.model import Aliased, APIModel, Unique, UnixDateTime, prevent_enum_error

from .character import (
    AgentSkill,
    AgentSkillItem,
    DiscSetEffect,
    WEngine,
    ZZZAgentProperty,
    ZZZAgentRank,
    ZZZBaseAgent,
    ZZZDisc,
    ZZZProperty,
    ZZZPropertyType,
    ZZZSkillType,
)

__all__ = (
    "DiscLevelCap",
    "LevelCapInfo",
    "PlanUnlockInfo",
    "RecommendedBuddy",
    "RecommendedBuild",
    "RecommendedBuildDetail",
    "RecommendedDiscProperty",
    "RecommendedDiscs",
    "RecommendedStat",
    "RecommendedTeam",
    "RecommendedTeamGroup",
    "RecommendedWeapon",
    "SkillLevelCap",
    "SkillUpgradeAdvice",
    "TeamAvatarExtInfo",
    "UpgradeGuideAgentDetail",
    "UpgradeGuideAgentInfo",
    "UpgradeGuideAgentProperty",
    "UpgradeGuideAgentSkill",
    "UpgradeGuideAwakenInfo",
    "UpgradeGuideBaseAgent",
    "UpgradeGuideDisc",
    "UpgradeGuideDiscSetEffect",
    "UpgradeGuideProperty",
    "UpgradeGuideSkillItem",
    "UpgradeGuideUser",
    "UpgradeGuideWEngine",
    "WikiEntry",
    "ZZZAgentUpgradeGuide",
    "ZZZUpgradeGuideAgent",
)


class UpgradeGuideBaseAgent(ZZZBaseAgent):
    """Base agent model returned by the upgrade guide tool."""

    square_icon: typing.Optional[str] = Aliased("role_square_url", default=None)  # type: ignore[assignment]
    sub_element: int = Aliased("sub_element_type")
    awaken_state: str


class UpgradeGuideAgentInfo(UpgradeGuideBaseAgent):
    """Brief agent info in the upgrade guide tool."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""


class ZZZUpgradeGuideAgent(UpgradeGuideAgentInfo):
    """An entry in the upgrade guide tool's agent list."""

    unlocked: bool
    is_up: bool
    """Whether the agent is currently on a rate-up banner."""
    is_teaser: bool
    """Whether the agent is unreleased (teaser/preview only)."""
    is_top: bool

    @pydantic.model_validator(mode="before")
    @classmethod
    def __unnest_avatar(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        return {**values, **values.pop("avatar", {})}


class UpgradeGuideAgentProperty(ZZZAgentProperty):
    """An agent stat in the upgrade guide tool."""

    final_val: str
    """The final value without formatting (e.g. percentages stripped)."""


class UpgradeGuideProperty(ZZZProperty):
    """A disc or W-engine property with upgrade guide detail."""

    level: int
    valid: bool
    system_id: int
    add: int


class UpgradeGuideSkillItem(AgentSkillItem):
    """An agent skill item in the upgrade guide tool."""

    awaken: bool


class UpgradeGuideAgentSkill(AgentSkill):
    """ZZZ agent skill model in the upgrade guide tool."""

    items: typing.Sequence[UpgradeGuideSkillItem]


class UpgradeGuideDiscSetEffect(DiscSetEffect):
    """A disc set effect in the upgrade guide tool."""

    icon: str
    count: int = Aliased("cnt")
    rarity: str


class UpgradeGuideDisc(ZZZDisc):
    """A ZZZ disc in the upgrade guide tool."""

    properties: typing.Sequence[UpgradeGuideProperty]
    main_properties: typing.Sequence[UpgradeGuideProperty]
    set_effect: UpgradeGuideDiscSetEffect = Aliased("equip_suit")
    invalid_property_cnt: int
    all_hit: bool


class UpgradeGuideWEngine(WEngine):
    """A ZZZ W-engine in the upgrade guide tool."""

    refinement: int = Aliased("star")  # type: ignore[assignment]
    """Can be 0 when the W-engine is a recommendation the user does not own."""
    properties: typing.Sequence[UpgradeGuideProperty]
    main_properties: typing.Sequence[UpgradeGuideProperty]


class SkillUpgradeAdvice(APIModel):
    """Recommended skill upgrade priority, grouped into tiers of skill types."""

    first: typing.Sequence[int]
    second: typing.Sequence[int]
    third: typing.Sequence[int]


class UpgradeGuideAwakenInfo(APIModel):
    """Agent awaken (potential) system availability info."""

    has_potential: bool = Aliased("has_awaken_system")
    current_level: int = Aliased("awaken_level")
    max_level: int = Aliased("awaken_max_level")


class UpgradeGuideAgentDetail(UpgradeGuideBaseAgent):
    """Detailed agent info (current build) in the upgrade guide tool."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""
    properties: typing.Sequence[UpgradeGuideAgentProperty]
    skills: typing.Sequence[UpgradeGuideAgentSkill]
    ranks: typing.Sequence[ZZZAgentRank]
    """Also known as Mindscape Cinemas in-game."""
    signature_weapon_id: int
    skill_upgrade: SkillUpgradeAdvice
    promotes: int
    """Current ascension (promotion) level."""
    unlock: bool
    awaken_info: typing.Optional[UpgradeGuideAwakenInfo] = Aliased("skill_awaken", default=None)
    """``None`` for agents the user has not unlocked."""


class RecommendedStat(APIModel):
    """A target stat range in a recommended build."""

    name: str = Aliased("property_name")
    type: typing.Union[int, ZZZPropertyType] = Aliased("property_id")
    low: str
    mid: str
    high: str
    show_phase: int
    show_percent: int

    @pydantic.field_validator("type", mode="before")
    def __cast_id(cls, v: int) -> typing.Union[int, ZZZPropertyType]:
        return prevent_enum_error(v, ZZZPropertyType)


class RecommendedDiscProperty(APIModel):
    """A recommended disc main or sub stat."""

    name: str = Aliased("property_name")
    type: typing.Union[int, ZZZPropertyType] = Aliased("property_id")
    system_id: int

    @pydantic.field_validator("type", mode="before")
    def __cast_id(cls, v: int) -> typing.Union[int, ZZZPropertyType]:
        return prevent_enum_error(v, ZZZPropertyType)


class RecommendedWeapon(APIModel):
    """The recommended W-engine for a build."""

    main: typing.Optional[UpgradeGuideWEngine] = None
    backup: typing.Optional[UpgradeGuideWEngine] = None

    @pydantic.field_validator("main", "backup", mode="before")
    def __nullify_placeholder(cls, v: typing.Any) -> typing.Any:
        # The API returns an empty object (id 0) when there is no recommendation.
        if isinstance(v, typing.Mapping) and not typing.cast("typing.Mapping[str, typing.Any]", v).get("id"):
            return None
        return typing.cast("typing.Any", v)


class RecommendedDiscs(APIModel):
    """The recommended discs for a build."""

    sets: typing.Sequence[UpgradeGuideDiscSetEffect] = Aliased("equip")
    set_kind: int = Aliased("equip_suit_kind")
    slot_4_main_stats: typing.Sequence[RecommendedDiscProperty] = Aliased("main_properties_4")
    slot_5_main_stats: typing.Sequence[RecommendedDiscProperty] = Aliased("main_properties_5")
    slot_6_main_stats: typing.Sequence[RecommendedDiscProperty] = Aliased("main_properties_6")
    sub_stats: typing.Sequence[RecommendedDiscProperty] = Aliased("sub_properties")


class RecommendedBuddy(APIModel, Unique):
    """A recommended bangboo in a team comp."""

    id: int
    name: str
    rarity: str


class TeamAvatarExtInfo(APIModel):
    """Extra info about an agent slot in a recommended team comp."""

    backup_avatar_list: typing.Sequence[typing.Any]
    pos_type: int


class RecommendedTeamGroup(APIModel):
    """A recommended team (main or backup variant)."""

    agents: typing.Sequence[UpgradeGuideAgentInfo] = Aliased("avatar_list")
    buddies: typing.Sequence[RecommendedBuddy] = Aliased("buddy_list")
    ext_info: typing.Sequence[TeamAvatarExtInfo] = Aliased("team_avatar_ext_info")


class RecommendedTeam(APIModel):
    """Recommended team comps for a build."""

    main: RecommendedTeamGroup
    backup: RecommendedTeamGroup


class WikiEntry(APIModel, Unique):
    """A HoYoLAB wiki link."""

    id: int
    url: str


class PlanUnlockInfo(APIModel):
    """Which agents, bangboos, and W-engines referenced by a build the user owns."""

    avatars: typing.Mapping[int, bool] = Aliased("avatar")
    buddies: typing.Mapping[int, bool] = Aliased("buddy")
    weapons: typing.Mapping[int, bool] = Aliased("weapon")


class RecommendedBuildDetail(APIModel):
    """The contents of a recommended build."""

    target_stats: typing.Sequence[RecommendedStat] = Aliased("avatar")
    weapon: RecommendedWeapon
    discs: RecommendedDiscs = Aliased("equip")
    skills: typing.Sequence[UpgradeGuideAgentSkill] = Aliased("skill")
    team: RecommendedTeam
    avatar_wiki: typing.Sequence[WikiEntry]
    bangboo_wiki: typing.Sequence[WikiEntry]
    unlock_info: PlanUnlockInfo
    unlocked_talents: typing.Sequence[int]


class RecommendedBuild(APIModel, Unique):
    """A recommended build for an agent."""

    id: int
    name: str
    description: str = Aliased("desc")
    released_at: UnixDateTime
    detail: typing.Optional[RecommendedBuildDetail] = Aliased("item", default=None)


class DiscLevelCap(APIModel):
    """Max disc level per rarity."""

    b: int
    a: int
    s: int


class SkillLevelCap(APIModel):
    """Max level for a skill type."""

    type: ZZZSkillType = Aliased("skill_type")
    level: int


class LevelCapInfo(APIModel):
    """Level caps for the current (or next) game version."""

    avatar_level_max: int
    weapon_level_max: int
    equip_level_max: DiscLevelCap
    skill_core_level_max: int
    skill_normal_level_max: typing.Sequence[SkillLevelCap]


class UpgradeGuideUser(APIModel):
    """The HoYoLAB user who owns the queried account."""

    aid: str
    name: str
    avatar: str
    level: int
    jump_url: str
    uid: str


class ZZZAgentUpgradeGuide(APIModel):
    """Detailed agent build and recommended upgrade guide."""

    avatar: UpgradeGuideAgentDetail
    discs: typing.Sequence[UpgradeGuideDisc] = Aliased("equip")
    weapon: typing.Optional[UpgradeGuideWEngine] = None
    plan: RecommendedBuild
    """The recommended build (upgrade guide)."""
    level_caps: typing.Optional[LevelCapInfo] = Aliased("item_info", default=None)
    """``None`` for agents the user has not unlocked."""
    next_level_caps: typing.Optional[LevelCapInfo] = Aliased("next_item_info", default=None)
    """``None`` for agents the user has not unlocked."""
    user: UpgradeGuideUser
    my_plan_id: str
    my_plan_list: typing.Sequence[typing.Any]
    valid_property_cnt: int
    from_my_plan: bool
    is_followed: bool
    new_feed_plan_flag: bool
    old_plan: bool
    plan_changed: bool
    plan_deleted: bool
    plan_only_special_property: bool
