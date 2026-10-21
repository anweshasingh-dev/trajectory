"""Dedicated Task Master forms using the application's shared CSRF protection."""
import sqlite3
from datetime import date
from flask import Blueprint, abort, render_template, request, url_for, redirect
from pydantic import ValidationError
from . import task_service, task_storage
from .task_deadlines import DEADLINE_CHOICES, task_details

bp = Blueprint("task_master", __name__)


def form_values() -> dict:
    if any(len(request.form.getlist(key)) != 1 for key in request.form):
        raise ValueError("Submit one value for each field.")
    return request.form.to_dict()


def expected_revision(values: dict) -> int:
    raw = values.get("revision", "")
    if not raw.isascii() or not raw.isdecimal() or len(raw) > 19:
        raise ValueError("Reload the saved task before submitting this form.")
    revision = int(raw)
    task_service.validate_revision(revision)
    return revision


@bp.errorhandler(sqlite3.Error)
def unavailable(error):
    return render_template(
        "task_master.html", tasks=None, notice=None,
        error="Your tasks could not be loaded. Reload this page to try again.",
    ), 503


def render_index(error=None, notice=None, status=200):
    today = date.today()
    tasks = [task_details(task, today) for task in task_storage.list_tasks()]
    return render_template("task_master.html", tasks=tasks, error=error, notice=notice), status


@bp.get("/tasks")
def index():
    notices = {
        "saved": "Task saved.",
        "deleted": "Task permanently deleted.",
        "absent": "This task has already been deleted.",
        "done": "Task marked done.",
        "undone": "Task marked undone.",
    }
    return render_index(notice=notices.get(request.args.get("result")))


@bp.route("/tasks/new", methods=["GET", "POST"])
@bp.route("/tasks/<task_id>/edit", methods=["GET", "POST"])
def edit(task_id=None):
    task = task_storage.find_task(task_id) if task_id else None
    if task:
        task = task_details(task, date.today())
    if request.method == "GET" and task_id and task is None:
        abort(404)
    values = dict(task) if task else {}
    revision = task["revision"] if task else ""
    errors, status, conflict = {}, 200, False
    if request.method == "POST":
        values = request.form.to_dict()
        revision = values.get("revision", "")
        try:
            submitted = form_values()
            expected = expected_revision(submitted) if task_id else None
            controls = {"csrf_token", "revision"} if task_id else {"csrf_token"}
            data = {key: value for key, value in submitted.items() if key not in controls}
            task_service.save_task(data, task_id, expected)
            return redirect(url_for("task_master.index", result="saved"), code=303)
        except ValidationError as error:
            errors = {
                str(item["loc"][0]) if item["loc"] else "form": item["msg"]
                for item in error.errors()
            }
            status = 422
        except ValueError as error:
            errors, status = {"form": str(error)}, 422
        except task_service.TaskConflict as error:
            errors, status, conflict = {"form": str(error)}, 409, True
        except sqlite3.Error:
            errors, status = {
                "form": "The database could not save your task. Your entries remain below; try again."
            }, 503
    return render_template(
        "task_form.html", task=task, task_id=task_id, values=values,
        revision=revision, errors=errors, conflict=conflict, deadline_choices=DEADLINE_CHOICES,
    ), status


@bp.post("/tasks/<task_id>/status")
def status(task_id):
    try:
        values = form_values()
        if set(values) - {"csrf_token", "revision", "status"}:
            raise ValueError("Unexpected fields in the status request.")
        task_service.set_status(task_id, values.get("status"), expected_revision(values))
        return redirect(url_for("task_master.index", result=values["status"]), code=303)
    except ValueError as failure:
        return render_index(error=str(failure), status=422)
    except task_service.TaskConflict as failure:
        return render_index(error=str(failure), status=409)
    except sqlite3.Error:
        return render_index(
            error="Status change did not save. Review the saved status below and try again.",
            status=503,
        )


@bp.route("/tasks/<task_id>/delete", methods=["GET", "POST"])
def delete(task_id):
    task = task_storage.find_task(task_id)
    if task:
        task = task_details(task, date.today())
    if request.method == "GET" and task is None:
        abort(404)
    revision = task["revision"] if task else ""
    error, status, conflict = None, 200, False
    if request.method == "POST":
        revision = request.form.get("revision", "")
        try:
            values = form_values()
            if set(values) - {"csrf_token", "revision", "confirmed"}:
                raise ValueError("Unexpected fields in the deletion request.")
            removed = task_service.remove_task(
                task_id, expected_revision(values), values.get("confirmed") == "on",
            )
            return redirect(
                url_for("task_master.index", result="deleted" if removed else "absent"), code=303,
            )
        except ValueError as failure:
            error, status = str(failure), 422
        except task_service.TaskConflict as failure:
            error, status, conflict = str(failure), 409, True
        except sqlite3.Error:
            error, status = "Deletion did not complete. Your task remains saved; try again.", 503
    return render_template(
        "task_delete.html", task=task, revision=revision,
        error=error, conflict=conflict,
    ), status
