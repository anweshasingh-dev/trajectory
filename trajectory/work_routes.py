"""Direct milestone/task forms; shared CSRF protection applies to every POST."""
import sqlite3
from flask import Blueprint, abort, redirect, render_template, request, url_for
from pydantic import ValidationError
from . import storage, work_storage, work_service

bp = Blueprint("work", __name__)


@bp.route("/goals/<goal_id>/work")
def index(goal_id):
    goal = storage.find_goal(goal_id)
    if goal is None:
        abort(404)
    return render_template(
        "work.html", goal=goal, milestones=work_storage.milestones(goal_id),
        tasks=work_storage.tasks(goal_id), saved=request.args.get("saved") == "1"
    )


@bp.route("/goals/<goal_id>/work/<kind>/new", methods=["GET", "POST"])
@bp.route("/goals/<goal_id>/work/<kind>/<item_id>/edit", methods=["GET", "POST"])
def edit(goal_id, kind, item_id=None):
    if kind not in ("tasks", "milestones"):
        abort(404)
    goal = storage.find_goal(goal_id)
    item = work_storage.find_item(goal_id, kind, item_id) if item_id else None
    if goal is None or (item_id and item is None):
        abort(404)
    values = dict(item) if item else {}
    revision = item['work_revision'] if item else work_storage.revision(goal_id)
    errors, status = {}, 200
    if request.method == "POST":
        values = request.form.to_dict()
        revision = values.get("revision", "")
        try:
            data = {key: value for key, value in values.items() if key not in ("csrf_token", "revision")}
            work_service.save(goal_id, kind, item_id, int(revision), data)
            return redirect(url_for("work.index", goal_id=goal_id, saved=1), code=303)
        except ValidationError as error:
            errors = {(str(item["loc"][0]) if item["loc"] else "form"): item["msg"] for item in error.errors()}
            status = 422
        except ValueError as error:
            errors, status = {"form": str(error)}, 422
        except work_service.WorkConflict as error:
            errors, status = {"form": str(error)}, 409
        except sqlite3.Error:
            errors, status = {"form": "Unsaved: the database could not save your work. Your entries remain below."}, 503
    return render_template(
        "work_form.html", goal=goal, kind=kind, item=item, values=values, revision=revision,
        errors=errors, milestones=work_storage.milestones(goal_id)
    ), status
