"""HTTP pages for dated work entries and correction."""
import sqlite3
from datetime import date
from uuid import uuid4
from flask import Blueprint, abort, redirect, render_template, request, url_for
from pydantic import ValidationError
from . import progress_service, progress_storage, work_storage

bp = Blueprint("progress", __name__)


def selected_task(goal_id, task_id):
    task = progress_storage.find_task(goal_id, task_id)
    if task is None:
        abort(404)
    return task


@bp.route("/goals/<goal_id>/tasks/<task_id>/progress")
def detail(goal_id, task_id):
    task = selected_task(goal_id, task_id)
    entries = progress_storage.entries_for_task(task_id)
    return render_template(
        "task_progress.html", task=task, goal_id=goal_id, entries=list(reversed(entries)),
        summary=progress_service.fold_entries(entries), saved=request.args.get("saved") == "1"
    )


@bp.route("/goals/<goal_id>/tasks/<task_id>/entries/new", methods=["GET", "POST"])
@bp.route("/goals/<goal_id>/tasks/<task_id>/entries/<entry_id>/edit", methods=["GET", "POST"])
def edit(goal_id, task_id, entry_id=None):
    task = selected_task(goal_id, task_id)
    entry = progress_storage.find_entry(entry_id) if entry_id else None
    if entry_id and (entry is None or entry["task_id"] != task_id):
        abort(404)
    if task["archived"] and not entry_id:
        abort(409, description="This task is archived. You can correct its history.")
    suggested_outcome = request.args.get("outcome", "partial")
    if suggested_outcome not in ("partial", "completed", "reopened"):
        suggested_outcome = "partial"
    values = dict(entry) if entry else {
        "work_date": date.today().isoformat(), "outcome": suggested_outcome,
        "actual_minutes": "", "notes": "", "blocker_action": "none", "blocker_text": ""
    }
    revision = entry["revision"] if entry else work_storage.revision(goal_id)
    request_id = str(uuid4())
    errors, status = {}, 200
    if request.method == "POST":
        values = request.form.to_dict()
        revision = values.get("revision", "")
        request_id = values.get("request_id", "")
        try:
            data = {key: value for key, value in values.items()
                    if key not in ("csrf_token", "revision", "request_id")}
            progress_service.save_entry(
                goal_id, task_id, entry_id, int(revision), data, request_id
            )
            return redirect(url_for("progress.detail", goal_id=goal_id, task_id=task_id, saved=1), code=303)
        except ValidationError as error:
            errors = {(str(item["loc"][0]) if item["loc"] else "form"): item["msg"]
                      for item in error.errors()}
            status = 422
        except ValueError as error:
            errors, status = {"form": str(error)}, 422
        except progress_service.ProgressConflict as error:
            errors, status = {"form": str(error)}, 409
        except sqlite3.Error:
            errors, status = {"form": "Unsaved: the work entry could not be saved. Your entries remain below."}, 503
    return render_template(
        "progress_form.html", goal_id=goal_id, task=task, entry=entry,
        values=values, revision=revision, request_id=request_id, errors=errors
    ), status


@bp.route("/goals/<goal_id>/tasks/<task_id>/entries/<entry_id>/delete", methods=["POST"])
def delete(goal_id, task_id, entry_id):
    selected_task(goal_id, task_id)
    try:
        progress_service.remove_entry(
            goal_id, task_id, entry_id, int(request.form.get("revision", "0")),
            request.form.get("confirmed") == "on"
        )
        return redirect(url_for("progress.detail", goal_id=goal_id, task_id=task_id, saved=1), code=303)
    except (ValueError, progress_service.ProgressConflict) as error:
        message, status = str(error), 409
    except sqlite3.Error:
        message, status = "The entry could not be removed. Your history is unchanged.", 503
    task = selected_task(goal_id, task_id)
    entries = progress_storage.entries_for_task(task_id)
    return render_template(
        "task_progress.html", task=task, goal_id=goal_id, entries=list(reversed(entries)),
        summary=progress_service.fold_entries(entries), error=message
    ), status
