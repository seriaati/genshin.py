import typing

from genshin.models.model import Aliased, APIModel

__all__ = ("ChallengeBangboo",)


class ChallengeBangboo(APIModel):
    """Shiyu Defense bangboo model."""

    id: int
    rarity: typing.Literal["S", "A"]
    level: int
    icon: str = Aliased("bangboo_rectangle_url")
