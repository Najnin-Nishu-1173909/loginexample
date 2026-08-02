"""Student dashboard and project-management routes for LU-TODO."""

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from loginapp import app, db


def student_access_required():
    """Allow access only to logged-in students."""

    if "user_id" not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for("login"))

    if session.get("user_role") != "student":
        return render_template("access_denied.html"), 403

    return None


@app.route("/student/home")
def student_home():
    """Display owned projects, shared projects and task statistics."""

    access_response = student_access_required()

    if access_response is not None:
        return access_response

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        # Projects owned by this student.
        cursor.execute(
            """
            SELECT
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,
                u.first_name AS owner_first_name,
                u.last_name AS owner_last_name,
                COUNT(t.task_id) AS task_count,
                COUNT(t.task_id) FILTER (
                    WHERE t.is_complete = FALSE
                ) AS incomplete_count,
                COUNT(t.task_id) FILTER (
                    WHERE t.is_complete = TRUE
                ) AS complete_count,
                COUNT(t.task_id) FILTER (
                    WHERE
                        t.is_complete = FALSE
                        AND t.due_date IS NOT NULL
                        AND t.due_date < CURRENT_DATE
                ) AS overdue_count
            FROM projects p
            JOIN users u
                ON u.user_id = p.owner_id
            LEFT JOIN tasks t
                ON t.project_id = p.project_id
            WHERE p.owner_id = %s
            GROUP BY
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,
                u.first_name,
                u.last_name
            ORDER BY LOWER(p.project_name);
            """,
            (user_id,),
        )

        owned_projects = cursor.fetchall()

        # Projects shared with this student.
        cursor.execute(
            """
            SELECT
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,
                u.first_name AS owner_first_name,
                u.last_name AS owner_last_name,
                COUNT(t.task_id) AS task_count,
                COUNT(t.task_id) FILTER (
                    WHERE t.is_complete = FALSE
                ) AS incomplete_count,
                COUNT(t.task_id) FILTER (
                    WHERE t.is_complete = TRUE
                ) AS complete_count,
                COUNT(t.task_id) FILTER (
                    WHERE
                        t.is_complete = FALSE
                        AND t.due_date IS NOT NULL
                        AND t.due_date < CURRENT_DATE
                ) AS overdue_count
            FROM project_members pm
            JOIN projects p
                ON p.project_id = pm.project_id
            JOIN users u
                ON u.user_id = p.owner_id
            LEFT JOIN tasks t
                ON t.project_id = p.project_id
            WHERE
                pm.user_id = %s
                AND p.owner_id <> %s
            GROUP BY
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,
                u.first_name,
                u.last_name
            ORDER BY LOWER(p.project_name);
            """,
            (user_id, user_id),
        )

        shared_projects = cursor.fetchall()

        # Overall statistics for accessible projects.
        cursor.execute(
            """
            WITH accessible_projects AS (
                SELECT project_id
                FROM projects
                WHERE owner_id = %s

                UNION

                SELECT project_id
                FROM project_members
                WHERE user_id = %s
            )
            SELECT
                (
                    SELECT COUNT(*)
                    FROM projects
                    WHERE owner_id = %s
                ) AS owned_project_count,

                (
                    SELECT COUNT(*)
                    FROM project_members pm
                    JOIN projects p
                        ON p.project_id = pm.project_id
                    WHERE
                        pm.user_id = %s
                        AND p.owner_id <> %s
                ) AS shared_project_count,

                COUNT(t.task_id) AS total_task_count,

                COUNT(t.task_id) FILTER (
                    WHERE t.is_complete = FALSE
                ) AS incomplete_task_count,

                COUNT(t.task_id) FILTER (
                    WHERE t.is_complete = TRUE
                ) AS complete_task_count,

                COUNT(t.task_id) FILTER (
                    WHERE
                        t.is_complete = FALSE
                        AND t.due_date IS NOT NULL
                        AND t.due_date < CURRENT_DATE
                ) AS overdue_task_count
            FROM accessible_projects ap
            LEFT JOIN tasks t
                ON t.project_id = ap.project_id;
            """,
            (
                user_id,
                user_id,
                user_id,
                user_id,
                user_id,
            ),
        )

        statistics = cursor.fetchone()

    return render_template(
        "student_home.html",
        owned_projects=owned_projects,
        shared_projects=shared_projects,
        statistics=statistics,
    )


@app.route("/student/projects/create", methods=["POST"])
def student_create_project():
    """Create a private project owned by the student."""

    access_response = student_access_required()

    if access_response is not None:
        return access_response

    project_name = request.form.get(
        "project_name",
        "",
    ).strip()

    description = request.form.get(
        "description",
        "",
    ).strip()

    if not project_name:
        flash("Project name is required.", "danger")
        return redirect(url_for("student_home"))

    if len(project_name) > 150:
        flash(
            "Project name cannot exceed 150 characters.",
            "danger",
        )
        return redirect(url_for("student_home"))

    if len(description) > 2000:
        flash(
            "Project description cannot exceed 2,000 characters.",
            "danger",
        )
        return redirect(url_for("student_home"))

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT project_id
            FROM projects
            WHERE
                owner_id = %s
                AND LOWER(project_name) = LOWER(%s);
            """,
            (user_id, project_name),
        )

        if cursor.fetchone() is not None:
            flash(
                "You already own a project with this name.",
                "danger",
            )
            return redirect(url_for("student_home"))

        cursor.execute(
            """
            INSERT INTO projects (
                owner_id,
                project_name,
                description
            )
            VALUES (%s, %s, %s);
            """,
            (
                user_id,
                project_name,
                description or None,
            ),
        )

    flash(
        f'Project "{project_name}" was created successfully.',
        "success",
    )

    return redirect(url_for("student_home"))


@app.route(
    "/student/projects/<int:project_id>/edit",
    methods=["POST"],
)
def student_edit_project(project_id):
    """Edit a project only when it belongs to this student."""

    access_response = student_access_required()

    if access_response is not None:
        return access_response

    project_name = request.form.get(
        "project_name",
        "",
    ).strip()

    description = request.form.get(
        "description",
        "",
    ).strip()

    if not project_name:
        flash("Project name is required.", "danger")
        return redirect(url_for("student_home"))

    if len(project_name) > 150:
        flash(
            "Project name cannot exceed 150 characters.",
            "danger",
        )
        return redirect(url_for("student_home"))

    if len(description) > 2000:
        flash(
            "Project description cannot exceed 2,000 characters.",
            "danger",
        )
        return redirect(url_for("student_home"))

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        # Confirm ownership.
        cursor.execute(
            """
            SELECT project_id
            FROM projects
            WHERE
                project_id = %s
                AND owner_id = %s;
            """,
            (project_id, user_id),
        )

        if cursor.fetchone() is None:
            flash(
                "You can only edit projects that you own.",
                "danger",
            )
            return redirect(url_for("student_home"))

        # Prevent duplicate names for the same owner.
        cursor.execute(
            """
            SELECT project_id
            FROM projects
            WHERE
                owner_id = %s
                AND LOWER(project_name) = LOWER(%s)
                AND project_id <> %s;
            """,
            (
                user_id,
                project_name,
                project_id,
            ),
        )

        if cursor.fetchone() is not None:
            flash(
                "You already own another project with this name.",
                "danger",
            )
            return redirect(url_for("student_home"))

        cursor.execute(
            """
            UPDATE projects
            SET
                project_name = %s,
                description = %s
            WHERE
                project_id = %s
                AND owner_id = %s;
            """,
            (
                project_name,
                description or None,
                project_id,
                user_id,
            ),
        )

    flash(
        f'Project "{project_name}" was updated successfully.',
        "success",
    )

    return redirect(url_for("student_home"))


@app.route(
    "/student/projects/<int:project_id>/delete",
    methods=["POST"],
)
def student_delete_project(project_id):
    """Delete a project only when it belongs to this student."""

    access_response = student_access_required()

    if access_response is not None:
        return access_response

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM projects
            WHERE
                project_id = %s
                AND owner_id = %s
            RETURNING project_name;
            """,
            (
                project_id,
                session["user_id"],
            ),
        )

        deleted_project = cursor.fetchone()

    if deleted_project is None:
        flash(
            "You can only delete projects that you own.",
            "danger",
        )
    else:
        flash(
            f'Project "{deleted_project["project_name"]}" '
            "and its tasks were deleted.",
            "success",
        )

    return redirect(url_for("student_home"))