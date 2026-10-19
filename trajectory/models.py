"""Server-side goal input contract; blank optional fields remain unknown."""
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GoalInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=6000)
    desired_outcome: str = Field(default="", max_length=2000)
    starting_point: str = Field(default="", max_length=2000)
    weekly_hours: float | None = Field(default=None, gt=0, le=168, allow_inf_nan=False)
    target_date: date | None = None

    outcome_unknown: bool = False
    starting_point_unknown: bool = False
    hours_unknown: bool = False
    no_deadline: bool = False

    @model_validator(mode="after")
    def reject_conflicting_answers(self):
        for field, flag in (
            ("desired_outcome", "outcome_unknown"),
            ("starting_point", "starting_point_unknown"),
            ("weekly_hours", "hours_unknown"),
            ("target_date", "no_deadline"),
        ):
            if getattr(self, flag) and getattr(self, field) not in (None, ""):
                raise ValueError(f"Provide {field.replace('_', ' ')} or select its alternative, not both.")
        return self

    @field_validator("weekly_hours", "target_date", mode="before")
    @classmethod
    def blank_is_unknown(cls, value):
        return None if isinstance(value, str) and not value.strip() else value
