import typing
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


from typing import Any
from pydantic import field_validator, model_validator, ConfigDict, BaseModel, Field


class ExampleModel(BaseModel):
    """An example model."""

    model_config = ConfigDict(frozen=False)

    field_without_default: str
    """Shows the *[Required]* marker in the signature."""

    field_plain_with_validator: int = 100
    """Show standard field with type annotation."""

    field_with_validator_and_alias: str = Field("FooBar", alias="BarFoo", validation_alias="BarFoo")
    """Shows corresponding validator with link/anchor."""

    field_with_constraints_and_description: int = Field(
        default=5, ge=0, le=100, description="Shows constraints within doc string."
    )

    @field_validator("field_with_validator_and_alias", "field_without_default", mode="before")
    @classmethod
    def check_max_length_ten(cls, v) -> str:
        """Show corresponding field with link/anchor."""
        if len(v) >= 10:
            raise ValueError("No more than 10 characters allowed")
        return v

    @model_validator(mode="before")
    @classmethod
    def lowercase_only(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Ensure that the field without a default is lowercase."""
        if isinstance(data.get("field_without_default"), str):
            data["field_without_default"] = data["field_without_default"].lower()
        return data
