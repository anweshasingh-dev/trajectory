"""Goal workspace routes; persistence and validation live in separate layers."""
import secrets
import sqlite3
from uuid import uuid4
from flask import current_app
from . import draft_storage, planning, review_storage
from .ai import OllamaAdapter, InferenceError
from flask import Blueprint, abort, redirect, render_template, request, session, url_for
from pydantic import ValidationError
from . import services, storage
from .clarification import FLAGS, questions_for

bp = Blueprint("goals", __name__)
FIELDS = ("title", "description", "desired_outcome", "starting_point", "weekly_hours", "target_date")


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


@bp.app_context_processor
def template_helpers():
    return {"csrf_token": csrf_token, "generation_id": lambda: str(uuid4())}


@bp.before_app_request
def protect_forms():
    if request.method == "POST":
        supplied = request.form.get("csrf_token", "")
        if not supplied or not secrets.compare_digest(supplied, session.get("csrf_token", "")):
            abort(400, description="This form expired. Reload the page before saving.")


@bp.route("/")
def index():
    return render_template("workspace.html", goals=storage.list_goals(), goal=None)


@bp.route("/goals/<goal_id>")
def detail(goal_id):
    goal = storage.find_goal(goal_id)
    if goal is None:
        abort(404)
    return render_template("workspace.html", goals=storage.list_goals(), goal=goal,
                           saved=request.args.get("saved") == "1", questions=questions_for(goal),
                           draft=review_storage.draft_for_review(latest["id"]) if (latest := draft_storage.latest_draft(goal_id)) else None,
                           approved=review_storage.current_plan(goal_id))


@bp.route("/goals/new", methods=["GET", "POST"])
@bp.route("/goals/<goal_id>/edit", methods=["GET", "POST"])
def edit(goal_id=None):
    goal = storage.find_goal(goal_id) if goal_id else None
    if goal_id and goal is None:
        abort(404)
    values = dict(goal) if goal else dict.fromkeys(FIELDS, "")
    errors, status = {}, 200
    if request.method == "POST":
        values = request.form.to_dict()
        try:
            revision = int(values.get("revision", "0"))
            saved_id = services.save_goal(
                {**{key: values.get(key, "") for key in FIELDS},
                 **{flag: values.get(flag) == "on" for flag in FLAGS}}, goal_id, revision
            )
            return redirect(url_for("goals.detail", goal_id=saved_id, saved=1), code=303)
        except ValidationError as error:
            errors = {(str(item["loc"][0]) if item["loc"] else "form"): item["msg"] for item in error.errors()}
            status = 422
        except (ValueError, services.StaleGoalError) as error:
            errors = {"form": str(error)}
            status = 409
        except sqlite3.Error:
            errors = {"form": "Unsaved: the database could not save your goal. Your entries remain below; please retry."}
            status = 503
    return render_template("goal_form.html", values=values, errors=errors, goal=goal), status


@bp.route("/goals/<goal_id>/generate", methods=["POST"])
def generate(goal_id):
    goal = storage.find_goal(goal_id)
    if goal is None:
        abort(404)
    try:
        adapter = OllamaAdapter(current_app.config["OLLAMA_MODEL"],
                                current_app.config["INFERENCE_TIMEOUT"])
        planning.generate_draft(goal_id, int(request.form.get("revision", "0")),
                                request.form.get("request_id", ""), adapter)
        return redirect(url_for("goals.detail", goal_id=goal_id), code=303)
    except (ValueError, planning.DraftConflict) as error:
        message, status = str(error), 409
    except InferenceError as error:
        message, status = str(error), 502
    except sqlite3.Error:
        message, status = "The draft could not be saved. Your previous saved work is unchanged; please retry.", 503
    goal = storage.find_goal(goal_id)
    if goal is None:
        abort(404)
    return render_template("workspace.html", goals=storage.list_goals(), goal=goal,
                           questions=questions_for(goal),
                           draft=review_storage.draft_for_review(latest["id"]) if (latest := draft_storage.latest_draft(goal_id)) else None,
                           approved=review_storage.current_plan(goal_id),
                           generation_error=message), status
