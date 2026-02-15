import typing

import pydantic

from genshin.models.model import Aliased, APIModel
from genshin.models.zzz.chronicle.events import ZZZGachaEventType

__all__ = (
    "ZZZGachaBannerInfo",
    "ZZZGachaCurrencies",
    "ZZZGachaInfo",
)


class ZZZGachaCurrencies(APIModel):
    """ZZZ gacha currency counts."""

    monochrome: int
    polychrome: int
    encrypted_master_tape: int
    master_tape: int
    boopon: int


class ZZZGachaBannerInfo(APIModel):
    """ZZZ gacha banner info model."""

    type: ZZZGachaEventType = Aliased("gacha_type")
    pity: int = Aliased("more_s_need_cnt")
    """Number of pulls needed until guaranteed S."""


class ZZZGachaInfo(APIModel):
    """ZZZ gacha info model."""

    currencies: ZZZGachaCurrencies
    banners: list[ZZZGachaBannerInfo] = Aliased("gacha_info_list")

    @pydantic.model_validator(mode="before")
    @classmethod
    def __convert_currencies(cls, data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        currency_mapping = {
            "GACHA_TICKET_TYPE_RECHARGE_MONOCHROME": "monochrome",
            "GACHA_TICKET_TYPE_POLYCHROME": "polychrome",
            "GACHA_TICKET_TYPE_ENCRYPTED_MASTER_TAPE": "encrypted_master_tape",
            "GACHA_TICKET_TYPE_MASTER_TAPE": "master_tape",
            "GACHA_TICKET_TYPE_BOOPON": "boopon",
        }

        tickets = data.get("tickets", [])
        converted_currencies = {
            currency_mapping[ticket["ticket_type"]]: ticket["ticket_cnt"]
            for ticket in tickets
            if ticket["ticket_type"] in currency_mapping
        }
        data["currencies"] = converted_currencies
        return data
