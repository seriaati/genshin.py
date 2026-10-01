"""Genshin TCG card plaza models."""

from __future__ import annotations

import enum
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, UnixDateTime, Unique, prevent_enum_error

__all__ = [
    "TCGDeck",
    "TCGDeckActionCard",
    "TCGDeckActionCardEffect",
    "TCGDeckCard",
    "TCGDeckCardType",
    "TCGDeckCharacterCard",
    "TCGDeckComment",
    "TCGDeckElement",
    "TCGDeckLabel",
    "TCGDeckSkill",
    "TCGDeckSkillCost",
    "TCGDiceType",
]


class TCGDeckElement(enum.IntEnum):
    """TCG card plaza character element."""

    CRYO = 301
    HYDRO = 302
    PYRO = 303
    ELECTRO = 304
    GEO = 305
    DENDRO = 306
    ANEMO = 307


class TCGDeckCardType(enum.IntEnum):
    """TCG card plaza card type."""

    CHARACTER = 0
    """Not returned by the API, character cards come from a separate endpoint."""
    EQUIPMENT = 2
    EVENT = 5
    SUPPORT = 6


class TCGDiceType(enum.IntEnum):
    """TCG card plaza dice cost type."""

    ENERGY = 1
    MATCHING = 3
    ARCANE_LEGEND = 6
    UNALIGNED = 10
    CRYO = 11
    HYDRO = 12
    PYRO = 13
    ELECTRO = 14
    GEO = 15
    DENDRO = 16
    ANEMO = 17


SPECIAL_ENERGY_TYPES = {19, 20}
"""Character-specific energy, such as Mavuika's Fighting Spirit and Skirk's Serpent's Subtlety."""


def _parse_dice_type(value: typing.Union[str, int]) -> typing.Union[TCGDiceType, int]:
    value = int(value)
    if value in SPECIAL_ENERGY_TYPES:
        return TCGDiceType.ENERGY
    return prevent_enum_error(value, TCGDiceType)


class TCGDeckLabel(APIModel, Unique):
    """TCG card plaza label, such as a game mode or a boss challenge."""

    id: int
    name: str
    is_hot: bool
    children: typing.Sequence[TCGDeckLabel]


class TCGDeckCard(APIModel, Unique):
    """TCG card plaza card."""

    id: int = Aliased("item_id")
    name: str
    icon: str
    small_icon: str = Aliased("icon_small")
    wiki_url: str
    max_count: int = Aliased("max_cnt")

    @pydantic.model_validator(mode="before")
    def __flatten_basic(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        return {**values, **values.get("basic", {})}


class TCGDeckCharacterCard(TCGDeckCard):
    """TCG card plaza character card."""

    element: typing.Union[TCGDeckElement, int]
    health: int = Aliased("hp")
    burst_cost: int = Aliased("skill_cost")
    """Energy required to use the elemental burst."""

    @pydantic.field_validator("element", mode="before")
    def __parse_element(cls, value: int) -> typing.Union[TCGDeckElement, int]:
        return prevent_enum_error(value, TCGDeckElement)


class TCGDeckActionCard(TCGDeckCard):
    """TCG card plaza action card."""

    type: typing.Union[TCGDeckCardType, int] = Aliased("card_type")
    tags: typing.Sequence[int] = Aliased("card_tag")

    cost_type: typing.Optional[typing.Union[TCGDiceType, int]] = Aliased("skill_element")
    cost: int = Aliased("skill_value")
    secondary_cost_type: typing.Optional[typing.Union[TCGDiceType, int]] = Aliased("skill_element2")
    secondary_cost: int = Aliased("skill_value2")
    energy_cost: int

    @pydantic.field_validator("type", mode="before")
    def __parse_type(cls, value: int) -> typing.Union[TCGDeckCardType, int]:
        return prevent_enum_error(value, TCGDeckCardType)

    @pydantic.field_validator("tags", mode="before")
    def __parse_tags(cls, value: typing.Sequence[str]) -> typing.Sequence[int]:
        return [int(tag) for tag in value if tag]

    @pydantic.field_validator("cost_type", "secondary_cost_type", mode="before")
    def __parse_cost_type(cls, value: str) -> typing.Optional[typing.Union[TCGDiceType, int]]:
        return _parse_dice_type(value) if value else None


class TCGDeckActionCardEffect(APIModel):
    """TCG card plaza action card effect."""

    description: str = Aliased("desc")
    """Description with HTML tags."""
    access: str
    """How to obtain the card."""

    cost_type: typing.Optional[typing.Union[TCGDiceType, int]] = Aliased("cost1_type_raw")
    cost: int = Aliased("cost1_raw")
    secondary_cost_type: typing.Optional[typing.Union[TCGDiceType, int]] = Aliased("cost2_type_raw")
    secondary_cost: int = Aliased("cost2_raw")

    @pydantic.field_validator("cost_type", "secondary_cost_type", mode="before")
    def __parse_cost_type(cls, value: str) -> typing.Optional[typing.Union[TCGDiceType, int]]:
        return _parse_dice_type(value) if value else None


class TCGDeck(APIModel):
    """TCG card plaza deck."""

    id: str
    title: str
    description: str = Aliased("desc")
    tags: typing.Sequence[str]
    label_ids: typing.Sequence[int]
    share_code: str = Aliased("card_code")
    created_at: UnixDateTime

    author_id: int = Aliased("account_uid")
    author_nickname: str = Aliased("nickname")
    author_icon: str = Aliased("avatar_url")

    character_cards: typing.Sequence[TCGDeckCharacterCard] = Aliased("role_cards")
    action_cards: typing.Sequence[TCGDeckActionCard]
    """Action cards in the deck, duplicates included."""

    video_url: str = Aliased("video_os_url")
    video_cover_url: str

    likes: int = Aliased("like_cnt")
    comments: int = Aliased("comment_cnt")
    favorites: int = Aliased("favour_cnt")
    views: int = Aliased("view_cnt")


class TCGDeckSkillCost(APIModel):
    """TCG card plaza character skill cost."""

    type: typing.Union[TCGDiceType, int] = Aliased("cost_type")
    icon: str
    value: int = Aliased("cost_num")

    @pydantic.field_validator("type", mode="before")
    def __parse_type(cls, value: str) -> typing.Union[TCGDiceType, int]:
        return _parse_dice_type(value)


class TCGDeckSkill(APIModel, Unique):
    """TCG card plaza character skill."""

    id: int
    name: str
    icon: str
    types: typing.Sequence[str] = Aliased("type")
    description: str = Aliased("rich_desc")
    """Description with HTML tags."""
    costs: typing.Sequence[TCGDeckSkillCost] = Aliased("cost_types")


class TCGDeckComment(APIModel):
    """Comment on a TCG card plaza deck."""

    id: int = Aliased("reply_id")
    content: str
    time: UnixDateTime = Aliased("reply_time")

    author_id: int
    author_nickname: str
    author_icon: str

    likes: int = Aliased("like_num")
    replies: typing.Sequence[TCGDeckComment] = Aliased("sub_reply_list")
    reply_count: int = Aliased("reply_num")

    @pydantic.model_validator(mode="before")
    def __flatten(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        user = values.get("user", {})
        content = values.get("content", {})
        return {
            **values,
            "author_id": user.get("account_uid"),
            "author_nickname": user.get("nickname"),
            "author_icon": user.get("avatar_path"),
            "content": content.get("text"),
        }
