import datetime
import typing

import pydantic

from genshin.models.model import Aliased, APIModel, DateTime
from genshin.models.zzz.character import ZZZElementType, ZZZSpecialty

__all__ = (
    "AnnihilationSimulacrum",
    "AnnihilationSimulacrumAgent",
    "AnnihilationSimulacrumBoss",
    "AnnihilationSimulacrumChallenge",
    "AnnihilationSimulacrumMedal",
)


class AnnihilationSimulacrumMedal(APIModel):
    """ZZZ Annihilation Simulacrum medal model."""

    id: int = Aliased("medal_id")
    icon: str = Aliased("medal_icon")
    no_damage_taken: bool = Aliased("is_no_injured")


class AnnihilationSimulacrumBoss(APIModel):
    """ZZZ Annihilation Simulacrum boss model."""

    icon: str
    name: str
    medal: AnnihilationSimulacrumMedal


class AnnihilationSimulacrumAgent(APIModel):
    """ZZZ Annihilation Simulacrum agent model."""

    id: int
    level: int
    element: ZZZElementType = Aliased("element_type")
    sub_element: int = Aliased("sub_element_type")
    specialty: ZZZSpecialty = Aliased("avatar_profession")
    rarity: typing.Literal["S", "A"]
    mindscape: int = Aliased("rank")
    icon: str = Aliased("role_square_url")


class AnnihilationSimulacrumChallenge(APIModel):
    """ZZZ Annihilation Simulacrum challenge model."""

    rank: int
    star: int
    duration: datetime.timedelta = Aliased("challenge_time")

    boss: AnnihilationSimulacrumBoss
    agents: typing.Sequence[AnnihilationSimulacrumAgent] = Aliased("avatar_list")

    @pydantic.field_validator("duration", mode="before")
    def __parse_duration(cls, value: typing.Mapping[str, typing.Any]) -> datetime.timedelta:
        return datetime.timedelta(
            days=value["day"], hours=value["hour"], minutes=value["minute"], seconds=value["second"]
        )


class AnnihilationSimulacrum(APIModel):
    """ZZZ Annihilation Simulacrum model."""

    start_time: typing.Optional[DateTime]
    end_time: typing.Optional[DateTime]

    challenges: typing.Sequence[AnnihilationSimulacrumChallenge] = Aliased("list")
    unlocked: bool = Aliased("unlock")
    refresh_time: datetime.timedelta
