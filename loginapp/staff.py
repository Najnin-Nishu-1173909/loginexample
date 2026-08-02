"""Staff dashboard and project-management routes for LU-TODO."""

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from loginapp import app, db


def staff_access_required():
    """Restrict a route to logged-in staff users.

    Returns:
        None when access is allowed.
        A Flask response when the user is not authorised.
    """

    if "user_id" not in session:
        flash(
            "Please log in to continue.",
            "warning",
        )
        return redirect(url_for("login"))

    if session.get("user_role") != "staff":
        return render_template("access_denied.html"), 403

    return None


@app.route("/staff/home")
def staff_home():
    """Display the staff dashboard.

    The dashboard includes:
    - projects owned by the current staff user;
    - projects shared with the current staff user;
    - task statistics;
    - project-member counts for owned projects.
    """

    access_response = staff_access_required()

    if access_response is not None:
        return access_response

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        # Projects owned by the current staff user.
        cursor.execute(
            """
            SELECT
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,

                COUNT(DISTINCT t.task_id) AS task_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE t.is_complete = FALSE
                ) AS incomplete_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE t.is_complete = TRUE
                ) AS complete_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE
                        t.is_complete = FALSE
                        AND t.due_date IS NOT NULL
                        AND t.due_date < CURRENT_DATE
                ) AS overdue_count,

                COUNT(DISTINCT pm.user_id) AS member_count

            FROM projects p

            LEFT JOIN tasks t
                ON t.project_id = p.project_id

            LEFT JOIN project_members pm
                ON pm.project_id = p.project_id

            WHERE p.owner_id = %s

            GROUP BY
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id

            ORDER BY LOWER(p.project_name);
            """,
            (user_id,),
        )

        owned_projects = cursor.fetchall()

        # Projects shared with the current staff user.
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
                owner.position AS owner_position,

                COUNT(DISTINCT t.task_id) AS task_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE t.is_complete = FALSE
                ) AS incomplete_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE t.is_complete = TRUE
                ) AS complete_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE
                        t.is_complete = FALSE
                        AND t.due_date IS NOT NULL
                        AND t.due_date < CURRENT_DATE
                ) AS overdue_count,

                COUNT(DISTINCT all_members.user_id) AS member_count

            FROM project_members current_membership

            JOIN projects p
                ON p.project_id = current_membership.project_id

            JOIN users owner
                ON owner.user_id = p.owner_id

            LEFT JOIN tasks t
                ON t.project_id = p.project_id

            LEFT JOIN project_members all_members
                ON all_members.project_id = p.project_id

            WHERE
                current_membership.user_id = %s
                AND p.owner_id <> %s

            GROUP BY
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,
                owner.first_name,
                owner.last_name,
                owner.email,
                owner.position

            ORDER BY LOWER(p.project_name);
            """,
            (
                user_id,
                user_id,
            ),
        )

        shared_projects = cursor.fetchall()

        # Overall statistics for all projects accessible to the staff user.
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
                    FROM project_members membership

                    JOIN projects project
                        ON project.project_id = membership.project_id

                    WHERE
                        membership.user_id = %s
                        AND project.owner_id <> %s
                ) AS shared_project_count,

                COUNT(task.task_id) AS total_task_count,

                COUNT(task.task_id) FILTER (
                    WHERE task.is_complete = FALSE
                ) AS incomplete_task_count,

                COUNT(task.task_id) FILTER (
                    WHERE task.is_complete = TRUE
                ) AS complete_task_count,

                COUNT(task.task_id) FILTER (
                    WHERE
                        task.is_complete = FALSE
                        AND task.due_date IS NOT NULL
                        AND task.due_date < CURRENT_DATE
                ) AS overdue_task_count

            FROM accessible_projects accessible

            LEFT JOIN tasks task
                ON task.project_id = accessible.project_id;
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
        "staff_home.html",
        owned_projects=owned_projects,
        shared_projects=shared_projects,
        statistics=statistics,
    )


@app.route(
    "/staff/projects/create",
    methods=["POST"],
)
def staff_create_project():
    """Create a project owned by the current staff user."""

    access_response = staff_access_required()

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
        flash(
            "Project name is required.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    if len(project_name) > 150:
        flash(
            "Project name cannot exceed 150 characters.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    if len(description) > 2000:
        flash(
            "Project description cannot exceed 2,000 characters.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        # Prevent duplicate project names for the same owner.
        cursor.execute(
            """
            SELECT project_id
            FROM projects
            WHERE
                owner_id = %s
                AND LOWER(project_name) = LOWER(%s);
            """,
            (
                user_id,
                project_name,
            ),
        )

        existing_project = cursor.fetchone()

        if existing_project is not None:
            flash(
                "You already own a project with this name.",
                "danger",
            )
            return redirect(url_for("staff_home"))

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
                description if description else None,
            ),
        )

    flash(
        f'Project "{project_name}" was created successfully.',
        "success",
    )

    return redirect(url_for("staff_home"))


@app.route(
    "/staff/projects/<int:project_id>/edit",
    methods=["POST"],
)
def staff_edit_project(project_id):
    """Edit a project owned by the current staff user.

    Staff cannot edit the name or description of a project that has
    only been shared with them.
    """

    access_response = staff_access_required()

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
        flash(
            "Project name is required.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    if len(project_name) > 150:
        flash(
            "Project name cannot exceed 150 characters.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    if len(description) > 2000:
        flash(
            "Project description cannot exceed 2,000 characters.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    user_id = session["user_id"]

    with db.get_cursor() as cursor:
        # Confirm that the current staff user owns this project.
        cursor.execute(
            """
            SELECT
                project_id,
                project_name
            FROM projects
            WHERE
                project_id = %s
                AND owner_id = %s;
            """,
            (
                project_id,
                user_id,
            ),
        )

        owned_project = cursor.fetchone()

        if owned_project is None:
            flash(
                "You can only edit projects that you own.",
                "danger",
            )
            return redirect(url_for("staff_home"))

        # Prevent duplicate names among the user's owned projects.
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

        duplicate_project = cursor.fetchone()

        if duplicate_project is not None:
            flash(
                "You already own another project with this name.",
                "danger",
            )
            return redirect(url_for("staff_home"))

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
                description if description else None,
                project_id,
                user_id,
            ),
        )

    flash(
        f'Project "{project_name}" was updated successfully.',
        "success",
    )

    return redirect(url_for("staff_home"))


@app.route(
    "/staff/projects/<int:project_id>/delete",
    methods=["POST"],
)
def staff_delete_project(project_id):
    """Delete a project owned by the current staff user.

    The database should automatically delete the project's tasks and
    memberships through cascading foreign-key relationships.
    """

    access_response = staff_access_required()

    if access_response is not None:
        return access_response

    user_id = session["user_id"]

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
                user_id,
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
            "and its tasks and memberships were deleted.",
            "success",
        )

    return redirect(url_for("staff_home"))