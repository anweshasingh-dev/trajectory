"""Translate labeled HTML inputs to bounded proposal JSON without losing invalid text."""
import copy
import json


def parse_form(form):
    count = int(form.get('milestone_count', '0'))
    if not 0 <= count <= 4:
        raise ValueError("A draft must have between one and four milestones.")
    proposal = {key: form.get(key, '') for key in ('summary', 'assumptions', 'questions')}
    for key in ('assumptions', 'questions'):
        proposal[key] = [line.strip() for line in proposal[key].splitlines() if line.strip()]
    proposal['milestones'] = []
    for m in range(count):
        prefix = f'm{m}_'
        task_count = int(form.get(prefix + 'task_count', '0'))
        if not 0 <= task_count <= 5:
            raise ValueError("Each milestone must have between one and five tasks.")
        milestone = {key: form.get(prefix + key, '') for key in ('title', 'completion_criterion')}
        milestone['tasks'] = []
        for t in range(task_count):
            milestone['tasks'].append({key: form.get(f'{prefix}t{t}_{key}', '')
                                      for key in ('title', 'description', 'estimated_minutes')})
        proposal['milestones'].append(milestone)
    return proposal


def validation_content(proposal):
    values = copy.deepcopy(proposal)
    for milestone in values['milestones']:
        for task in milestone['tasks']:
            raw = task['estimated_minutes']
            try:
                task['estimated_minutes'] = None if raw in ('', None) else int(raw)
            except (ValueError, TypeError) as error:
                raise ValueError("Suggested effort must be a whole number of minutes, or blank for unknown.") from error
    return json.dumps(values)
