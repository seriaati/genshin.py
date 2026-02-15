import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, Unique, prevent_enum_error

__all__ = (
    "AgentSkill",
    "AgentSkillItem",
    "DiscSetEffect",
    "WEngine",
    "ZZZAgentProperty",
    "ZZZAgentRank",
    "ZZZAwakenedPotential",
    "ZZZAwakenedPotentialInfo",
    "ZZZAwakenedPotentialSkill",
    "ZZZAwakenedPotentialSkillDetail",
    "ZZZBaseAgent",
    "ZZZDisc",
    "ZZZElementType",
    "ZZZFullAgent",
    "ZZZPartialAgent",
    "ZZZProperty",
    "ZZZPropertyType",
    "ZZZSkillType",
    "ZZZSpecialty",
)


class ZZZElementType(enum.IntEnum):
    """ZZZ element type."""

    PHYSICAL = 200
    FIRE = 201
    ICE = 202
    ELECTRIC = 203
    ETHER = 205


class ZZZSpecialty(enum.IntEnum):
    """ZZZ agent compatible specialty."""

    ATTACK = 1
    STUN = 2
    ANOMALY = 3
    SUPPORT = 4
    DEFENSE = 5
    RUPTURE = 6


class ZZZBaseAgent(APIModel, Unique):
    """ZZZ base agent model."""

    id: int  # 4 digit number
    element: ZZZElementType = Aliased("element_type")
    rarity: typing.Literal["S", "A"]
    name: str = Aliased("name_mi18n")
    full_name: str = Aliased("full_name_mi18n")
    specialty: ZZZSpecialty = Aliased("avatar_profession")
    faction_icon: str = Aliased("group_icon_path")
    rectangle_icon: str = Aliased("hollow_icon_path")
    square_icon: str = Aliased("role_square_url")


class ZZZPartialAgent(ZZZBaseAgent):
    """Character without any equipment."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""

    @property
    def banner_icon(self) -> str:
        return f"https://act-webstatic.hoyoverse.com/game_record/zzzv2/role_vertical_painting/role_vertical_painting_{self.id}.png"


class ZZZPropertyType(enum.IntEnum):
    """ZZZ property type."""

    # Agent prop
    AGENT_HP = 1
    AGENT_ATK = 2
    AGENT_DEF = 3
    AGENT_IMPACT = 4
    AGENT_CRIT_RATE = 5
    AGENT_CRIT_DMG = 6
    AGENT_ANOMALY_MASTERY = 7
    AGENT_ANOMALY_PROFICIENCY = 8
    AGENT_PEN_RATIO = 9
    AGENT_ENERGY_GEN = 11
    AGENT_PEN = 232
    AGENT_SHEER_FORCE = 19
    AGENT_ADRENALINE = 20

    # Agent DMG bonus
    PHYSICAL_DMG_BONUS = 315
    FIRE_DMG_BONUS = 316
    ICE_DMG_BONUS = 317
    ELECTRIC_DMG_BONUS = 318
    ETHER_DMG_BONUS = 319

    # Disc drive and w-engine
    CRIT_RATE = 20103
    CRIT_DMG = 21103

    ANOMALY_PROFICIENCY = 31203
    ANOMALY_MASTERY = 31402
    ENERGY_REGEN = 30502
    IMPACT = 12202

    BASE_ATK = 12101
    FLAT_HP = 11103
    FLAT_ATK = 12103
    FLAT_DEF = 13103
    FLAT_PEN = 23203

    HP_PERCENT = 11102
    ATK_PERCENT = 12102
    DEF_PERCENT = 13102
    PEN_PERCENT = 23103

    DISC_PHYSICAL_DMG_BONUS = 31503
    DISC_FIRE_DMG_BONUS = 31603
    DISC_ICE_DMG_BONUS = 31703
    DISC_ELECTRIC_DMG_BONUS = 31803
    DISC_ETHER_DMG_BONUS = 31903


class ZZZProperty(APIModel):
    """A property (stat) for disc or w-engine."""

    name: str = Aliased("property_name")
    type: typing.Union[int, ZZZPropertyType] = Aliased("property_id")
    value: str = Aliased("base")

    @pydantic.field_validator("type", mode="before")
    def __cast_id(cls, v: int) -> typing.Union[int, ZZZPropertyType]:
        return prevent_enum_error(v, ZZZPropertyType)


class ZZZAgentProperty(ZZZProperty):
    """A property model, but for agents."""

    add: str
    final: str


class DiscSetEffect(APIModel):
    """A disc set effect."""

    id: int = Aliased("suit_id")
    name: str
    owned_num: int = Aliased("own")
    two_piece_description: str = Aliased("desc1")
    four_piece_description: str = Aliased("desc2")


class WEngine(APIModel):
    """A ZZZ W-engine, it's like a weapon."""

    id: int
    level: int
    name: str
    icon: str
    refinement: typing.Literal[1, 2, 3, 4, 5] = Aliased("star")
    rarity: typing.Literal["B", "A", "S"]
    properties: typing.Sequence[ZZZProperty]
    main_properties: typing.Sequence[ZZZProperty]
    effect_title: str = Aliased("talent_title")
    effect_description: str = Aliased("talent_content")
    profession: ZZZSpecialty


class ZZZDisc(APIModel):
    """A ZZZ disc, like an artifact in Genshin."""

    id: int
    level: int
    name: str
    icon: str
    rarity: typing.Literal["B", "A", "S"]
    main_properties: typing.Sequence[ZZZProperty]
    properties: typing.Sequence[ZZZProperty]
    set_effect: DiscSetEffect = Aliased("equip_suit")
    position: int = Aliased("equipment_type")


class ZZZSkillType(enum.IntEnum):
    """ZZZ agent skill type."""

    BASIC_ATTACK = 0
    DODGE = 2
    ASSIST = 6
    SPECIAL_ATTACK = 1
    CHAIN_ATTACK = 3
    CORE_SKILL = 5


class AgentSkillItem(APIModel):
    """An agent skill item."""

    title: str
    text: str


class AgentSkill(APIModel):
    """ZZZ agent skill model."""

    level: int
    type: ZZZSkillType = Aliased("skill_type")
    items: typing.Sequence[AgentSkillItem]
    """One skill can have different forms (?), so there are multiple 'items'."""


class ZZZAgentRank(APIModel):
    """ZZZ agent rank model."""

    id: int
    name: str
    description: str = Aliased("desc")
    position: int = Aliased("pos")
    unlocked: bool = Aliased("is_unlocked")


class ZZZAwakenedPotentialSkillDetail(APIModel):
    """ZZZ awakened potential skill detail model."""

    name: str = Aliased("title")
    description: str = Aliased("text")


class ZZZAwakenedPotentialSkill(APIModel):
    """ZZZ awakened potential skill model."""

    type: ZZZSkillType = Aliased("skill_type")
    title: str = Aliased("awaken_simple_info")
    skill_details: typing.Sequence[ZZZAwakenedPotentialSkillDetail] = Aliased("skill_items")


class ZZZAwakenedPotential(APIModel):
    """ZZZ awakened potential model."""

    level: int = Aliased("awaken_level")
    name: str = Aliased("level_show_name")
    buffed_skills: typing.Sequence[ZZZAwakenedPotentialSkill] = Aliased("awaken_skill_items")


class ZZZAwakenedPotentialInfo(APIModel):
    """ZZZ agent awakened potential info model."""

    has_potential: bool = Aliased("has_awaken_system")
    current: int = Aliased("awaken_level")
    max: int = Aliased("awaken_max_level")
    items: typing.Sequence[ZZZAwakenedPotential] = Aliased("skill_awaken_items")


class ZZZFullAgent(ZZZBaseAgent):
    """Character with equipment."""

    level: int
    rank: int
    """Also known as Mindscape Cinema in-game."""
    faction_name: str = Aliased("camp_name_mi18n")
    properties: typing.Sequence[ZZZAgentProperty]
    discs: typing.Sequence[ZZZDisc] = Aliased("equip")
    w_engine: typing.Optional[WEngine] = Aliased("weapon", default=None)
    skills: typing.Sequence[AgentSkill]
    ranks: typing.Sequence[ZZZAgentRank]
    """Also known as Mindscape Cinemas in-game."""
    potential: ZZZAwakenedPotentialInfo = Aliased("skill_awaken")

    banner_icon: str = Aliased("role_vertical_painting_url")

    @staticmethod
    def _extract_skin_id(url: str) -> typing.Optional[int]:
        filename = url.split("/")[-1].split(".")[0]
        parts = filename.split("_")

        if len(parts) >= 5:
            return int(parts[-1])
        return None

    @property
    def outfit_id(self) -> typing.Optional[int]:
        return self._extract_skin_id(self.banner_icon)
