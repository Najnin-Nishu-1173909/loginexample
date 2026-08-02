"""System-wide shared-project administration routes for LU-TODO."""

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from loginapp import app, db


def admin_project_access_required():
    """Restrict system project administration to admin users.

    Returns:
        None when access is allowed.
        A Flask response when access is denied.
    """

    if "user_id" not in session:
        flash(
            "Please log in to continue.",
            "warning",
        )
        return redirect(url_for("login"))

    if session.get("user_role") != "admin":
        return render_template("access_denied.html"), 403

    return None


def get_shared_project(project_id):
    """Return a project only when it currently has at least one member.

    Private projects are deliberately excluded because administrators
    must not be able to administer unrelated private projects.
    """

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
                owner.position AS owner_position,
                owner.user_role AS owner_role,
                owner.status AS owner_status,

                (
                    SELECT COUNT(*)
                    FROM project_members pm
                    WHERE pm.project_id = p.project_id
                ) AS member_count

            FROM projects p

            JOIN users owner
                ON owner.user_id = p.owner_id

            WHERE
                p.project_id = %s

                AND EXISTS (
                    SELECT 1
                    FROM project_members pm
                    WHERE pm.project_id = p.project_id
                );
            """,
            (project_id,),
        )

        return cursor.fetchone()


@app.route("/admin/shared-projects")
def admin_shared_projects():
    """Show every shared project in the system.

    Only projects with at least one record in project_members are
    included. Private projects are not shown.
    """

    access_response = admin_project_access_required()

    if access_response is not None:
        return access_response

    search_term = request.args.get(
        "search",
        "",
    ).strip()

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
                owner.position AS owner_position,
                owner.user_role AS owner_role,
                owner.status AS owner_status,

                COUNT(DISTINCT pm.user_id) AS member_count,
                COUNT(DISTINCT t.task_id) AS task_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE t.is_complete = TRUE
                ) AS complete_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE t.is_complete = FALSE
                ) AS incomplete_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE
                        t.is_complete = FALSE
                        AND t.due_date IS NOT NULL
                        AND t.due_date < CURRENT_DATE
                ) AS overdue_count

            FROM projects p

            JOIN users owner
                ON owner.user_id = p.owner_id

            JOIN project_members pm
                ON pm.project_id = p.project_id

            LEFT JOIN tasks t
                ON t.project_id = p.project_id

            WHERE
                (
                    %s = ''

                    OR p.project_name ILIKE '%%' || %s || '%%'

                    OR COALESCE(
                        p.description,
                        ''
                    ) ILIKE '%%' || %s || '%%'

                    OR owner.first_name ILIKE '%%' || %s || '%%'

                    OR owner.last_name ILIKE '%%' || %s || '%%'

                    OR owner.email ILIKE '%%' || %s || '%%'
                )

            GROUP BY
                p.project_id,
                p.project_name,
                p.description,
                p.owner_id,
                owner.first_name,
                owner.last_name,
                owner.email,
                owner.position,
                owner.user_role,
                owner.status

            ORDER BY
                LOWER(p.project_name),
                LOWER(owner.last_name),
                LOWER(owner.first_name);
            """,
            (
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
            ),
        )

        shared_projects = cursor.fetchall()

        # Staff and admin accounts are the only eligible new owners.
        cursor.execute(
            """
            SELECT
                user_id,
                email,
                first_name,
                last_name,
                position,
                user_role,
                status
            FROM users
            WHERE user_role IN ('staff', 'admin')
            ORDER BY
                CASE user_role
                    WHEN 'staff' THEN 1
                    WHEN 'admin' THEN 2
                    ELSE 3
                END,
                LOWER(first_name),
                LOWER(last_name),
                LOWER(email);
            """
        )

        eligible_owners = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                COUNT(DISTINCT p.project_id)
                    AS shared_project_count,

                COUNT(DISTINCT pm.user_id)
                    AS total_membership_count,

                COUNT(DISTINCT t.task_id)
                    AS total_task_count,

                COUNT(DISTINCT t.task_id) FILTER (
                    WHERE
                        t.is_complete = FALSE
                        AND t.due_date IS NOT NULL
                        AND t.due_date < CURRENT_DATE
                ) AS overdue_task_count

            FROM projects p

            JOIN project_members pm
                ON pm.project_id = p.project_id

            LEFT JOIN tasks t
                ON t.project_id = p.project_id;
            """
        )

        statistics = cursor.fetchone()

    return render_template(
        "admin_system_projects.html",
        shared_projects=shared_projects,
        eligible_owners=eligible_owners,
        statistics=statistics,
        search_term=search_term,
    )


@app.route(
    "/admin/shared-projects/<int:project_id>/owner",
    methods=["POST"],
)
def admin_change_shared_project_owner(project_id):
    """Transfer a shared project to a staff or admin user."""

    access_response = admin_project_access_required()

    if access_response is not None:
        return access_response

    project = get_shared_project(project_id)

    if project is None:
        flash(
            "The shared project could not be found. "
            "Private projects cannot be administered here.",
            "danger",
        )
        return redirect(url_for("admin_shared_projects"))

    new_owner_id_text = request.form.get(
        "new_owner_id",
        "",
    ).strip()

    try:
        new_owner_id = int(new_owner_id_text)
    except (TypeError, ValueError):
        flash(
            "Select a valid new owner.",
            "danger",
        )
        return redirect(url_for("admin_shared_projects"))

    if new_owner_id == project["owner_id"]:
        flash(
            "That user is already the project owner.",
            "warning",
        )
        return redirect(url_for("admin_shared_projects"))

    with db.get_cursor() as cursor:
        # Only staff and admin accounts may become project owners.
        cursor.execute(
            """
            SELECT
                user_id,
                email,
                first_name,
                last_name,
                user_role,
                status
            FROM users
            WHERE
                user_id = %s
                AND user_role IN ('staff', 'admin');
            """,
            (new_owner_id,),
        )

        new_owner = cursor.fetchone()

        if new_owner is None:
            flash(
                "The new owner must be a staff or admin user.",
                "danger",
            )
            return redirect(url_for("admin_shared_projects"))

        # Project names must remain unique for each owner.
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
                new_owner_id,
                project["project_name"],
                project_id,
            ),
        )

        conflicting_project = cursor.fetchone()

        if conflicting_project is not None:
            flash(
                f'{new_owner["first_name"]} '
                f'{new_owner["last_name"]} already owns a '
                f'project named "{project["project_name"]}". '
                "Rename one of the projects before transferring it.",
                "danger",
            )
            return redirect(url_for("admin_shared_projects"))

        # An owner must not also remain in project_members.
        cursor.execute(
            """
            DELETE FROM project_members
            WHERE
                project_id = %s
                AND user_id = %s;
            """,
            (
                project_id,
                new_owner_id,
            ),
        )

        cursor.execute(
            """
            UPDATE projects
            SET owner_id = %s
            WHERE project_id = %s;
            """,
            (
                new_owner_id,
                project_id,
            ),
        )

    flash(
        f'Ownership of "{project["project_name"]}" was transferred '
        f'to {new_owner["first_name"]} {new_owner["last_name"]}.',
        "success",
    )

    return redirect(url_for("admin_shared_projects"))


@app.route(
    "/admin/shared-projects/<int:project_id>/delete",
    methods=["POST"],
)
def admin_delete_shared_project(project_id):
    """Delete any shared project from the system.

    The database's cascading foreign keys should also remove all tasks
    and project-membership records belonging to the project.
    """

    access_response = admin_project_access_required()

    if access_response is not None:
        return access_response

    project = get_shared_project(project_id)

    if project is None:
        flash(
            "The shared project could not be found. "
            "Private projects cannot be deleted from this page.",
            "danger",
        )
        return redirect(url_for("admin_shared_projects"))

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM projects
            WHERE
                project_id = %s

                AND EXISTS (
                    SELECT 1
                    FROM project_members pm
                    WHERE pm.project_id = projects.project_id
                )

            RETURNING project_name;
            """,
            (project_id,),
        )

        deleted_project = cursor.fetchone()

    if deleted_project is None:
        flash(
            "The project is no longer shared or has already been deleted.",
            "warning",
        )
    else:
        flash(
            f'Shared project "{deleted_project["project_name"]}" '
            "and all of its tasks and memberships were deleted.",
            "success",
        )

    return redirect(url_for("admin_shared_projects"))