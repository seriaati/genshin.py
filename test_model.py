from typing import Any
import typing
from pydantic import field_validator, model_validator, ConfigDict, BaseModel, Field
import pydantic


class StokenResult(pydantic.BaseModel):
    """Result of fetching `stoken` with `fetch_stoken_by_game_token`."""

    aid: str
    mid: str
    token: str

    @pydantic.model_validator(mode="before")
    def _transform_result(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        return {
            "aid": values["user_info"]["aid"],
            "mid": values["user_info"]["mid"],
            "token": values["token"]["token"],
        }
