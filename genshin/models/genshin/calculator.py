"""Genshin calculator models."""

from __future__ import annotations

import collections
import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, Unique

from . import character

__all__ = [
    "CALCULATOR_ARTIFACTS",
    "CALCULATOR_ELEMENTS",
    "CALCULATOR_WEAPON_TYPES",
    "CalculatorArtifact",
    "CalculatorArtifactResult",
    "CalculatorCharacter",
    "CalculatorCharacterDetails",
    "CalculatorConsumable",
    "CalculatorFurnishing",
    "CalculatorFurnishingResults",
    "CalculatorResult",
    "CalculatorTalent",
    "CalculatorWeapon",
]

CALCULATOR_ELEMENTS: typing.Mapping[int, str] = {
    1: "Pyro",
    2: "Anemo",
    3: "Geo",
    4: "Dendro",
    5: "Electro",
    6: "Hydro",
    7: "Cryo",
}
CALCULATOR_WEAPON_TYPES: typing.Mapping[int, str] = {
    0: "Unknown",
    1: "Sword",
    10: "Catalyst",
    11: "Claymore",
    12: "Bow",
    13: "Polearm",
}
CALCULATOR_ARTIFACTS: typing.Mapping[int, str] = {
    1: "Flower of Life",
    2: "Plume of Death",
    3: "Sands of Eon",
    4: "Goblet of Eonothem",
    5: "Circlet of Logos",
}


class MaterialSource(str, enum.Enum):
    """Source of the material."""

    SPECIAL = "MT_SPECIAL"
    MONSTER = "MT_MONSTER"
    WORLD = "MT_WORLD"
    DOMAIN = "MT_DUNGEON"
    WEEKLY_BOSS = "MT_WEEKLY_DUNGEON"


class PartialCalculatorCharacter(APIModel):
    id: int
    icon: str
    rarity: int = Aliased("avatar_level")


class PartialCalculatorWeapon(APIModel):
    id: int
    icon: str
    rarity: int = Aliased("weapon_level")


class CalculatorCharacter(character.BaseCharacter):
    """Character meant to be used with calculators."""

    element: str = Aliased("element_attr_id")
    weapon_type: str = Aliased("weapon_cat_id")
    level: int = Aliased("level_current", default=0)
    max_level: int

    @pydantic.field_validator("element", mode="before")
    def __parse_element(cls, v: typing.Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_ELEMENTS[int(v)]

    @pydantic.field_validator("weapon_type", mode="before")
    def __parse_weapon_type(cls, v: typing.Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorWeapon(APIModel, Unique):
    """Weapon meant to be used with calculators."""

    id: int
    name: str
    icon: str
    rarity: int = Aliased("weapon_level")
    type: str = Aliased("weapon_cat_id")
    level: int = Aliased("level_current", default=0)
    max_level: int

    @pydantic.field_validator("type", mode="before")
    def __parse_weapon_type(cls, v: typing.Any) -> str:
        if isinstance(v, str):
            return v

        return CALCULATOR_WEAPON_TYPES[int(v)]


class CalculatorArtifact(APIModel, Unique):
    """Artifact meant to be used with calculators."""

    id: int
    name: str
    icon: str
    rarity: int = Aliased("reliquary_level")
    pos: int = Aliased("reliquary_cat_id")
    level: int = Aliased("level_current", default=0)
    max_level: int

    @property
    def pos_name(self) -> str:
        return CALCULATOR_ARTIFACTS[self.pos]


class CalculatorTalent(APIModel, Unique):
    """Talent of a character meant to be used with calculators."""

    id: int
    group_id: int  # proudSkillGroupId
    name: str
    icon: str
    level: int = Aliased("level_current", default=0)
    max_level: int

    @property
    def type(self) -> typing.Literal["attack", "skill", "burst", "passive", "dash"] | None:
        """The type of the talent, parsed from the group id.

        Does not work for traveler!
        """
        # special cases
        if self.id == self.group_id:
            return "passive"  # maybe hoyo does this for unapgradables?

        if len(str(self.id)) == 6:  # in candSkillDepotIds
            return "attack"

        # 4139 -> group=41 identifier=3 order=9
        _, relevant = divmod(self.group_id, 100)
        identifier, order = divmod(relevant, 10)

        if identifier == 2:
            return "passive"
        elif order == 1:
            return "attack"
        elif order == 2:
            return "skill"
        elif order == 9:
            return "burst"
        elif order == 3:
            return "dash"
        else:
            return None

    @property
    def upgradeable(self) -> bool:
        """Whether this talent can be leveled up."""
        return self.type not in ("passive", "dash")

    def __int__(self) -> int:
        return self.group_id


class CalculatorFurnishing(APIModel, Unique):
    """Furnishing meant to be used with calculators."""

    id: int
    name: str
    icon: str = Aliased("icon_url")
    rarity: int = Aliased("level")

    amount: typing.Optional[int] = Aliased("num", default=None)


class CalculatorCharacterDetails(APIModel):
    """Details of a synced calculator character."""

    weapon: CalculatorWeapon = Aliased("weapon")
    talents: typing.Sequence[CalculatorTalent] = Aliased("skill_list")
    artifacts: typing.Sequence[CalculatorArtifact] = Aliased("reliquary_list")

    @pydantic.field_validator("talents")
    def __correct_talent_current_level(cls, v: typing.Sequence[CalculatorTalent]) -> typing.Sequence[CalculatorTalent]:
        # passive talent have current levels at 0 for some reason
        talents: list[CalculatorTalent] = []

        for talent in v:
            if talent.max_level == 1 and talent.level == 0:
                raw = talent.model_dump()
                raw["level"] = 1
                talent = CalculatorTalent(**raw)

            talents.append(talent)

        return v

    @property
    def upgradeable_talents(self) -> typing.Sequence[CalculatorTalent]:
        """All talents that can be leveled up."""
        if self.talents[2].type == "dash":
            return (self.talents[0], self.talents[1], self.talents[3])
        else:
            return (self.talents[0], self.talents[1], self.talents[2])


class CalculatorConsumable(APIModel, Unique):
    """Item consumed when upgrading."""

    id: int
    name: str
    icon: str
    rarity: int = Aliased("level")
    amount: int = Aliased("num", default=1)
    lacking: int = Aliased("lack_num", default=0)
    wiki_url: str


class CalculatorArtifactResult(APIModel):
    """Calculation result for a specific artifact."""

    artifact_id: int = Aliased("reliquary_id")
    materials: typing.Sequence[CalculatorConsumable] = Aliased("id_consume_list")


class CalculatorTalentInfo(APIModel):
    """Information about a talent in the calculator."""

    talent_id: int = Aliased("id")
    current: int = Aliased("level_current", default=0)
    target: int = Aliased("level_target", default=0)


class CalculatorTalentResult(APIModel):
    """Calculation result for a specific talent."""

    info: CalculatorTalentInfo = Aliased("skill_info")
    materials: typing.Sequence[CalculatorConsumable] = Aliased("consume_list")


class CalculatorMonster(APIModel):
    """Monster that drops a material."""

    id: int = Aliased("monster_id")
    name: str = Aliased("monster_name")
    icon: str = Aliased("monster_icon")
    map_url: str = Aliased("monster_map_url")


class CalculatorDomain(APIModel):
    """Domain that drops a material."""

    name: str = Aliased("dungeon_name")
    weekdays: typing.Sequence[int] = Aliased("drop_day")
    """List of weekdays the domain is open, 0=Monday, 6=Sunday."""
    calendar_url: str = Aliased("calendar_link")


class RemainingMaterialDetail(APIModel):
    """Details of remaining required materials for a character."""

    materials: typing.Sequence[CalculatorConsumable] = Aliased("consume")

    characters: typing.Sequence[PartialCalculatorCharacter] = Aliased("avatars")
    """Characters these materials are needed for, empty if accessing weapons."""
    weapons: typing.Sequence[PartialCalculatorWeapon] = Aliased("weapons")
    """Weapons these materials are needed for, empty if accessing characters or talents."""

    material_source: MaterialSource

    monster: typing.Optional[CalculatorMonster] = None
    """Monster info, present if material_source is MT_MONSTER or MT_WEEKLY_DUNGEON."""
    map_url: typing.Optional[str] = None
    """URL to interactive map, present if material_source is MT_WORLD."""
    domain: typing.Optional[CalculatorDomain] = Aliased("dungeon_calendar", default=None)
    """Domain info, may be present if material_source is MT_DUNGEON."""


class RemainingMaterialDetails(APIModel):
    """Details of remaining required materials for a character."""

    characters: typing.Sequence[RemainingMaterialDetail] = Aliased("avatar_consume")
    weapon: typing.Sequence[RemainingMaterialDetail] = Aliased("weapon_consume")
    talents: typing.Sequence[RemainingMaterialDetail] = Aliased("avatar_skill_consume")


class CalculatorResult(APIModel):
    """Calculation result."""

    character: list[CalculatorConsumable] = Aliased("avatar_consume")
    weapon: list[CalculatorConsumable] = Aliased("weapon_consume")
    talents: list[CalculatorTalentResult] = Aliased("skills_consume")
    artifacts: list[CalculatorArtifactResult] = Aliased("reliquary_consume")

    lineup_recommendation: typing.Optional[str] = Aliased("lineup_recommend", default=None)

    @property
    def total(self) -> typing.Sequence[CalculatorConsumable]:
        talents = [i for t in self.talents for i in t.materials]
        artifacts = [i for a in self.artifacts for i in a.materials]
        combined = self.character + self.weapon + talents + artifacts

        grouped: dict[int, list[CalculatorConsumable]] = collections.defaultdict(list)
        for i in combined:
            grouped[i.id].append(i)

        total = [
            CalculatorConsumable(
                id=x[0].id,
                name=x[0].name,
                icon=x[0].icon,
                wiki_url=x[0].wiki_url,
                rarity=x[0].rarity,
                lacking=x[0].lacking,
                amount=sum(i.amount for i in x),
            )
            for x in grouped.values()
        ]

        return total


class CalculatorBatchResult(APIModel):
    """Batch calculation result."""

    characters: list[CalculatorResult] = Aliased("items")
    available_materials: list[CalculatorConsumable] = Aliased("available_material")
    total_materials: list[CalculatorConsumable] = Aliased("overall_consume")
    total_material_details: RemainingMaterialDetails = Aliased("overall_material_consume")
    individual_results: typing.Sequence[CalculatorBatchResult] = Aliased("single_role_result")

    has_user_info: bool

    @property
    def total_remaining_required_materials(self) -> typing.Sequence[CalculatorConsumable]:
        return [m for m in self.total_materials if m.lacking > 0]


class CalculatorFurnishingResults(APIModel):
    """Furnishing calculation result."""

    furnishings: list[CalculatorConsumable] = Aliased("list")

    @property
    def total(self) -> typing.Sequence[CalculatorConsumable]:
        return self.furnishings
