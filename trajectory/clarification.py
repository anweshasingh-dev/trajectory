"""Deterministic questions: never infer confirmed facts from goal prose."""
CONTEXT_FIELDS = (
    ("desired_outcome", "outcome_unknown", "What would finished look like?", "I am not sure yet"),
    ("starting_point", "starting_point_unknown", "Where are you starting?", "I am not sure yet"),
    ("weekly_hours", "hours_unknown", "How many hours per week are available?", "I do not know yet"),
    ("target_date", "no_deadline", "Do you have a specific target date?", "No fixed deadline"),
)
FLAGS = tuple(item[1] for item in CONTEXT_FIELDS)


def questions_for(goal):
    return [
        {"field": field, "question": question}
        for field, flag, question, _ in CONTEXT_FIELDS
        if goal[field] in (None, "") and not goal.get(flag, False)
    ]
