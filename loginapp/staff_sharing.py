"""Staff project-sharing and member-management routes for LU-TODO."""

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from loginapp import app, db


def staff_sharing_access_required():
    """Allow only logged-in staff users."""

    if "user_id" not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for("login"))

    if session.get("user_role") != "staff":
        return render_template("access_denied.html"), 403

    return None


def get_staff_owned_project(project_id):
    """Return a project only when the current staff user owns it."""

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                project_id,
                project_name,
                description,
                owner_id
            FROM projects
            WHERE
                project_id = %s
                AND owner_id = %s;
            """,
            (
                project_id,
                session["user_id"],
            ),
        )

        return cursor.fetchone()


@app.route("/staff/projects/<int:project_id>/members")
def staff_project_members(project_id):
    """Display members and available users for an owned project."""

    access_response = staff_sharing_access_required()

    if access_response is not None:
        return access_response

    project = get_staff_owned_project(project_id)

    if project is None:
        flash(
            "You can only manage sharing for projects that you own.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    with db.get_cursor() as cursor:
        # Current project members.
        cursor.execute(
            """
            SELECT
                u.user_id,
                u.email,
                u.first_name,
                u.last_name,
                u.position,
                u.profile_picture,
                u.user_role,
                u.status
            FROM project_members pm

            JOIN users u
                ON u.user_id = pm.user_id

            WHERE pm.project_id = %s

            ORDER BY
                LOWER(u.first_name),
                LOWER(u.last_name),
                LOWER(u.email);
            """,
            (project_id,),
        )

        members = cursor.fetchall()

        # Users who are not the owner and not already members.
        cursor.execute(
            """
            SELECT
                u.user_id,
                u.email,
                u.first_name,
                u.last_name,
                u.position,
                u.profile_picture,
                u.user_role,
                u.status
            FROM users u

            WHERE
                u.user_id <> %s

                AND NOT EXISTS (
                    SELECT 1
                    FROM project_members pm
                    WHERE
                        pm.project_id = %s
                        AND pm.user_id = u.user_id
                )

            ORDER BY
                CASE u.user_role
                    WHEN 'student' THEN 1
                    WHEN 'staff' THEN 2
                    WHEN 'admin' THEN 3
                END,
                LOWER(u.first_name),
                LOWER(u.last_name),
                LOWER(u.email);
            """,
            (
                session["user_id"],
                project_id,
            ),
        )

        available_users = cursor.fetchall()

    return render_template(
        "staff_members.html",
        project=project,
        members=members,
        available_users=available_users,
    )


@app.route(
    "/staff/projects/<int:project_id>/members/add",
    methods=["POST"],
)
def staff_add_project_members(project_id):
    """Share an owned project with one or more users."""

    access_response = staff_sharing_access_required()

    if access_response is not None:
        return access_response

    project = get_staff_owned_project(project_id)

    if project is None:
        flash(
            "You can only share projects that you own.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    selected_user_ids = request.form.getlist("user_ids")

    if not selected_user_ids:
        flash(
            "Select at least one user to add.",
            "danger",
        )
        return redirect(
            url_for(
                "staff_project_members",
                project_id=project_id,
            )
        )

    valid_user_ids = []

    for user_id_text in selected_user_ids:
        try:
            user_id = int(user_id_text)
        except (TypeError, ValueError):
            continue

        if user_id != session["user_id"]:
            valid_user_ids.append(user_id)

    if not valid_user_ids:
        flash(
            "No valid users were selected.",
            "danger",
        )
        return redirect(
            url_for(
                "staff_project_members",
                project_id=project_id,
            )
        )

    added_count = 0

    with db.get_cursor() as cursor:
        for user_id in set(valid_user_ids):
            # Confirm the selected user exists.
            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE user_id = %s;
                """,
                (user_id,),
            )

            selected_user = cursor.fetchone()

            if selected_user is None:
                continue

            cursor.execute(
                """
                INSERT INTO project_members (
                    project_id,
                    user_id
                )
                VALUES (%s, %s)
                ON CONFLICT (project_id, user_id)
                DO NOTHING
                RETURNING user_id;
                """,
                (
                    project_id,
                    user_id,
                ),
            )

            if cursor.fetchone() is not None:
                added_count += 1

    if added_count == 0:
        flash(
            "The selected users are already members, or could not be added.",
            "warning",
        )
    else:
        flash(
            f"{added_count} member"
            f"{'' if added_count == 1 else 's'} added successfully.",
            "success",
        )

    return redirect(
        url_for(
            "staff_project_members",
            project_id=project_id,
        )
    )


@app.route(
    "/staff/projects/<int:project_id>/"
    "members/<int:user_id>/remove",
    methods=["POST"],
)
def staff_remove_project_member(project_id, user_id):
    """Remove a member from a project owned by the current staff user."""

    access_response = staff_sharing_access_required()

    if access_response is not None:
        return access_response

    project = get_staff_owned_project(project_id)

    if project is None:
        flash(
            "You can only remove members from projects that you own.",
            "danger",
        )
        return redirect(url_for("staff_home"))

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM project_members
            WHERE
                project_id = %s
                AND user_id = %s
            RETURNING user_id;
            """,
            (
                project_id,
                user_id,
            ),
        )

        removed_member = cursor.fetchone()

    if removed_member is None:
        flash(
            "That user is not a member of this project.",
            "warning",
        )
    else:
        flash(
            "The member was removed from the project.",
            "success",
        )

    return redirect(
        url_for(
            "staff_project_members",
            project_id=project_id,
        )
    )