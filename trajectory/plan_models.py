"""Bounded AI proposal contract. No dates, acceptance or database IDs from AI."""
from pydantic import BaseModel, ConfigDict, Field


class ProposalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, strict=True)


class ProposedTask(ProposalModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=1200)
    estimated_minutes: int | None = Field(ge=1, le=10080)


class ProposedMilestone(ProposalModel):
    title: str = Field(min_length=1, max_length=160)
    completion_criterion: str = Field(min_length=1, max_length=800)
    tasks: list[ProposedTask] = Field(min_length=1, max_length=5)


class PlanProposal(ProposalModel):
    summary: str = Field(min_length=1, max_length=1200)
    assumptions: list[str] = Field(max_length=6)
    questions: list[str] = Field(max_length=6)
    milestones: list[ProposedMilestone] = Field(min_length=1, max_length=4)

    # Individual notes must also be bounded before storage/display.
    @classmethod
    def validate_response(cls, content):
        proposal = cls.model_validate_json(content)
        if any(not note.strip() or len(note) > 500 for note in proposal.assumptions + proposal.questions):
            raise ValueError("Invalid proposal notes")
        return proposal
