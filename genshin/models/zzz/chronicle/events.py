import typing
from enum import Enum

import pydantic

from genshin.models.model import Aliased, APIModel, UnixDateTime, prevent_enum_error
from genshin.models.zzz.character import ZZZElementType, ZZZSpecialty

__all__ = (
    "ZZZCharacterGachaEvent",
    "ZZZEvent",
    "ZZZEventStatus",
    "ZZZGachaCalendar",
    "ZZZGachaEvent",
    "ZZZGachaEventCharacter",
    "ZZZGachaEventStatus",
    "ZZZGachaEventType",
    "ZZZGachaEventWeapon",
    "ZZZWeaponGachaEvent",
)


class ZZZEventStatus(Enum):
    """ZZZ event status enum."""

    IN_PROGRESS = "STATE_IN_PROGRESS"
    COMPLETED = "STATE_COMPLETED"
    NOT_STARTED = "STATE_NOT_START"


class ZZZGachaEventStatus(Enum):
    """ZZZ gacha event status enum."""

    IN_PROGRESS = "GACHA_STATE_IN_PROGRESS"
    COMPLETED = "GACHA_STATE_COMPLETED"
    NOT_STARTED = "GACHA_STATE_NOT_START"


class ZZZGachaEventType(Enum):
    """ZZZ gacha event type enum."""

    CHARACTER = "GACHA_TYPE_CHARACTER_UP"
    WEAPON = "GACHA_TYPE_WEAPON_UP"
    PERMANENT = "GACHA_TYPE_PERMANENT"
    BANGBOO = "GACHA_TYPE_BANGBOO"
    EXCLUSIVE_RESCREENING = "GACHA_TYPE_CHARACTER_RETURN"
    REVERBERATION = "GACHA_TYPE_WEAPON_RETURN"


class ZZZEvent(APIModel):
    """ZZZ event calendar event."""

    id: int = Aliased("activity_id")
    status: typing.Union[ZZZEventStatus, str] = Aliased("state")
    name: str

    obtained_monochromes: int = Aliased("monochrome_got_cnt")
    max_monochromes: int = Aliased("monochrome_cnt")

    start: UnixDateTime = Aliased("start_ts")
    end: UnixDateTime = Aliased("end_ts")

    seconds_until_start: int = Aliased("left_start_ts")
    seconds_until_end: int = Aliased("left_end_ts")

    @pydantic.field_validator("status", mode="before")
    def __validate_status(cls, v: str) -> typing.Union[ZZZEventStatus, str]:
        return prevent_enum_error(v, ZZZEventStatus)


class ZZZGachaEvent(APIModel):
    """ZZZ gacha event model."""

    type: typing.Union[ZZZGachaEventType, str] = Aliased("gacha_type")
    status: typing.Union[ZZZGachaEventStatus, str] = Aliased("gacha_state")
    version: str
    """Like 2.4, 2.5."""

    start: UnixDateTime = Aliased("start_ts")
    end: UnixDateTime = Aliased("end_ts")

    seconds_until_start: int = Aliased("left_start_ts")
    seconds_until_end: int = Aliased("left_end_ts")

    # No clue what these are
    sup_lock_show: bool
    insurance_id: int

    @pydantic.field_validator("type", mode="before")
    def __validate_type(cls, v: str) -> typing.Union[ZZZGachaEventType, str]:
        return prevent_enum_error(v, ZZZGachaEventType)

    @pydantic.field_validator("status", mode="before")
    def __validate_status(cls, v: str) -> typing.Union[ZZZGachaEventStatus, str]:
        return prevent_enum_error(v, ZZZGachaEventStatus)


class ZZZGachaEventCharacter(APIModel):
    """ZZZ gacha event character."""

    id: int = Aliased("avatar_id")
    name: str = Aliased("avatar_name")
    full_name: str

    rarity: typing.Literal["S", "A"]
    icon: str
    specialty: ZZZSpecialty = Aliased("avatar_profession")
    element: ZZZElementType = Aliased("avatar_element_type")
    sub_element: int = Aliased("avatar_sub_element_type")  # Probably like Miyabi's Frost

    wiki_url: str
    jump_cultivate: bool
    is_forward: bool
    show_upon: bool


class ZZZGachaEventWeapon(APIModel):
    """ZZZ gacha event weapon."""

    id: int = Aliased("weapon_id")
    rarity: typing.Literal["S", "A"]
    icon: str
    specialty: ZZZSpecialty = Aliased("profession")

    skill_name: str = Aliased("talent_title")
    skill_description: str = Aliased("talent_content")

    wiki_url: str
    show_upon: bool


class ZZZCharacterGachaEvent(ZZZGachaEvent):
    """ZZZ gacha event for characters."""

    characters: typing.Sequence[ZZZGachaEventCharacter] = Aliased("avatar_list")


class ZZZWeaponGachaEvent(ZZZGachaEvent):
    """ZZZ gacha event for weapons."""

    weapons: typing.Sequence[ZZZGachaEventWeapon] = Aliased("weapon_list")


class ZZZGachaCalendar(APIModel):
    """ZZZ gacha calendar model."""

    characters: typing.Sequence[ZZZCharacterGachaEvent] = Aliased("avatar_gacha_schedule_list")
    weapons: typing.Sequence[ZZZWeaponGachaEvent] = Aliased("weapon_gacha_schedule_list")
