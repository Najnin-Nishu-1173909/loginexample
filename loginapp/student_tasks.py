"""Student project-detail and task-management routes for LU-TODO."""

from datetime import date

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from loginapp import app
from loginapp import db


VALID_PRIORITIES = {
    "low",
    "medium",
    "high",
}


def student_task_access_required():
    """Restrict student task routes to logged-in students."""

    if "user_id" not in session:
        flash(
            "Please log in to continue.",
            "warning",
        )
        return redirect(url_for("login"))

    if session.get("user_role") != "student":
        return render_template("access_denied.html"), 403

    return None


def get_accessible_project(project_id):
    """Return a project if the student owns it or is a member.

    Returns None when the project does not exist or the current
    student does not have permission to access it.
    """

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,
                owner.first_name AS owner_first_name,
                owner.last_name AS owner_last_name,
                owner.email AS owner_email,
                (p.owner_id = %s) AS is_owner
            FROM projects p

            JOIN users owner
                ON owner.user_id = p.owner_id

            WHERE
                p.project_id = %s
                AND (
                    p.owner_id = %s
                    OR EXISTS (
                        SELECT 1
                        FROM project_members pm
                        WHERE
                            pm.project_id = p.project_id
                            AND pm.user_id = %s
                    )
                );
            """,
            (
                user_id,
                project_id,
                user_id,
                user_id,
            ),
        )

        return cursor.fetchone()


def get_accessible_task(project_id, task_id):
    """Return a task only if it belongs to an accessible project."""

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                t.task_id,
                t.project_id,
                t.task_name,
                t.description,
                t.priority,
                t.due_date,
                t.is_complete
            FROM tasks t

            JOIN projects p
                ON p.project_id = t.project_id

            WHERE
                t.task_id = %s
                AND t.project_id = %s
                AND (
                    p.owner_id = %s
                    OR EXISTS (
                        SELECT 1
                        FROM project_members pm
                        WHERE
                            pm.project_id = p.project_id
                            AND pm.user_id = %s
                    )
                );
            """,
            (
                task_id,
                project_id,
                user_id,
                user_id,
            ),
        )

        return cursor.fetchone()


def validate_task_form(form):
    """Validate task form data.

    Returns:
        A tuple containing:
        - cleaned task name;
        - cleaned description or None;
        - priority;
        - parsed due date or None;
        - error message or None.
    """

    task_name = form.get(
        "task_name",
        "",
    ).strip()

    description = form.get(
        "description",
        "",
    ).strip()

    priority = form.get(
        "priority",
        "",
    ).strip().lower()

    due_date_text = form.get(
        "due_date",
        "",
    ).strip()

    if not task_name:
        return None, None, None, None, (
            "Task name is required."
        )

    if len(task_name) > 200:
        return None, None, None, None, (
            "Task name cannot exceed 200 characters."
        )

    if len(description) > 2000:
        return None, None, None, None, (
            "Task description cannot exceed 2,000 characters."
        )

    if priority not in VALID_PRIORITIES:
        return None, None, None, None, (
            "Select a valid priority: low, medium, or high."
        )

    parsed_due_date = None

    if due_date_text:
        try:
            parsed_due_date = date.fromisoformat(
                due_date_text
            )
        except ValueError:
            return None, None, None, None, (
                "Enter a valid due date."
            )

    return (
        task_name,
        description if description else None,
        priority,
        parsed_due_date,
        None,
    )


@app.route(
    "/student/projects/<int:project_id>/tasks"
)
def student_project_detail(project_id):
    """Show an accessible project and all of its tasks."""

    access_response = student_task_access_required()

    if access_response is not None:
        return access_response

    project = get_accessible_project(project_id)

    if project is None:
        flash(
            "The project could not be found, or you do not "
            "have permission to access it.",
            "danger",
        )
        return redirect(url_for("student_home"))

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                task_id,
                project_id,
                task_name,
                description,
                priority,
                due_date,
                is_complete,
                (
                    is_complete = FALSE
                    AND due_date IS NOT NULL
                    AND due_date < CURRENT_DATE
                ) AS is_overdue
            FROM tasks
            WHERE project_id = %s
            ORDER BY
                is_complete ASC,
                CASE
                    WHEN (
                        is_complete = FALSE
                        AND due_date IS NOT NULL
                        AND due_date < CURRENT_DATE
                    )
                    THEN 0
                    ELSE 1
                END,
                due_date ASC NULLS LAST,
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                LOWER(task_name);
            """,
            (project_id,),
        )

        tasks = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_count,

                COUNT(*) FILTER (
                    WHERE is_complete = TRUE
                ) AS complete_count,

                COUNT(*) FILTER (
                    WHERE is_complete = FALSE
                ) AS incomplete_count,

                COUNT(*) FILTER (
                    WHERE
                        is_complete = FALSE
                        AND due_date IS NOT NULL
                        AND due_date < CURRENT_DATE
                ) AS overdue_count
            FROM tasks
            WHERE project_id = %s;
            """,
            (project_id,),
        )

        statistics = cursor.fetchone()

    return render_template(
        "student_project.html",
        project=project,
        tasks=tasks,
        statistics=statistics,
    )


@app.route(
    "/student/projects/<int:project_id>/tasks/create",
    methods=["POST"],
)
def student_create_task(project_id):
    """Add a task to an owned or shared project."""

    access_response = student_task_access_required()

    if access_response is not None:
        return access_response

    project = get_accessible_project(project_id)

    if project is None:
        flash(
            "You do not have permission to add tasks "
            "to this project.",
            "danger",
        )
        return redirect(url_for("student_home"))

    (
        task_name,
        description,
        priority,
        due_date,
        error,
    ) = validate_task_form(request.form)

    if error:
        flash(error, "danger")
        return redirect(
            url_for(
                "student_project_detail",
                project_id=project_id,
            )
        )

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO tasks (
                project_id,
                task_name,
                description,
                priority,
                due_date,
                is_complete
            )
            VALUES (%s, %s, %s, %s, %s, FALSE);
            """,
            (
                project_id,
                task_name,
                description,
                priority,
                due_date,
            ),
        )

    flash(
        f'Task "{task_name}" was added successfully.',
        "success",
    )

    return redirect(
        url_for(
            "student_project_detail",
            project_id=project_id,
        )
    )


@app.route(
    "/student/projects/<int:project_id>/"
    "tasks/<int:task_id>/edit",
    methods=["POST"],
)
def student_edit_task(project_id, task_id):
    """Edit a task in an owned or shared project."""

    access_response = student_task_access_required()

    if access_response is not None:
        return access_response

    task = get_accessible_task(
        project_id,
        task_id,
    )

    if task is None:
        flash(
            "The task could not be found, or you do not "
            "have permission to edit it.",
            "danger",
        )
        return redirect(url_for("student_home"))

    (
        task_name,
        description,
        priority,
        due_date,
        error,
    ) = validate_task_form(request.form)

    if error:
        flash(error, "danger")
        return redirect(
            url_for(
                "student_project_detail",
                project_id=project_id,
            )
        )

    is_complete = (
        request.form.get("is_complete") == "on"
    )

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE tasks
            SET
                task_name = %s,
                description = %s,
                priority = %s,
                due_date = %s,
                is_complete = %s
            WHERE
                task_id = %s
                AND project_id = %s;
            """,
            (
                task_name,
                description,
                priority,
                due_date,
                is_complete,
                task_id,
                project_id,
            ),
        )

    flash(
        f'Task "{task_name}" was updated successfully.',
        "success",
    )

    return redirect(
        url_for(
            "student_project_detail",
            project_id=project_id,
        )
    )


@app.route(
    "/student/projects/<int:project_id>/"
    "tasks/<int:task_id>/toggle",
    methods=["POST"],
)
def student_toggle_task(project_id, task_id):
    """Mark a task complete or change it back to incomplete."""

    access_response = student_task_access_required()

    if access_response is not None:
        return access_response

    task = get_accessible_task(
        project_id,
        task_id,
    )

    if task is None:
        flash(
            "The task could not be found, or you do not "
            "have permission to update it.",
            "danger",
        )
        return redirect(url_for("student_home"))

    new_status = not task["is_complete"]

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE tasks
            SET is_complete = %s
            WHERE
                task_id = %s
                AND project_id = %s;
            """,
            (
                new_status,
                task_id,
                project_id,
            ),
        )

    if new_status:
        message = (
            f'Task "{task["task_name"]}" was marked complete.'
        )
    else:
        message = (
            f'Task "{task["task_name"]}" was reopened.'
        )

    flash(message, "success")

    return redirect(
        url_for(
            "student_project_detail",
            project_id=project_id,
        )
    )


@app.route(
    "/student/projects/<int:project_id>/"
    "tasks/<int:task_id>/delete",
    methods=["POST"],
)
def student_delete_task(project_id, task_id):
    """Delete a task from an owned or shared project."""

    access_response = student_task_access_required()

    if access_response is not None:
        return access_response

    task = get_accessible_task(
        project_id,
        task_id,
    )

    if task is None:
        flash(
            "The task could not be found, or you do not "
            "have permission to delete it.",
            "danger",
        )
        return redirect(url_for("student_home"))

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM tasks
            WHERE
                task_id = %s
                AND project_id = %s;
            """,
            (
                task_id,
                project_id,
            ),
        )

    flash(
        f'Task "{task["task_name"]}" was deleted.',
        "success",
    )

    return redirect(
        url_for(
            "student_project_detail",
            project_id=project_id,
        )
    )