"""Administrator user-management routes for LU-TODO."""

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from loginapp import app, db


VALID_USER_ROLES = {
    "student",
    "staff",
    "admin",
}

VALID_USER_STATUSES = {
    "active",
    "inactive",
}


def admin_user_access_required():
    """Restrict user-administration routes to logged-in admins.

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


def get_managed_user(user_id):
    """Return a user and useful account statistics.

    Returns None if the user does not exist.
    """

    with db.get_cursor() as cursor:
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
                u.status,

                (
                    SELECT COUNT(*)
                    FROM projects p
                    WHERE p.owner_id = u.user_id
                ) AS owned_project_count,

                (
                    SELECT COUNT(*)
                    FROM project_members pm
                    WHERE pm.user_id = u.user_id
                ) AS shared_project_count,

                (
                    SELECT COUNT(*)
                    FROM tasks t

                    JOIN projects p
                        ON p.project_id = t.project_id

                    WHERE p.owner_id = u.user_id
                ) AS owned_task_count,

                (
                    SELECT COUNT(*)
                    FROM tasks t

                    JOIN projects p
                        ON p.project_id = t.project_id

                    WHERE
                        p.owner_id = u.user_id
                        AND t.is_complete = FALSE
                ) AS incomplete_owned_task_count

            FROM users u

            WHERE u.user_id = %s;
            """,
            (user_id,),
        )

        return cursor.fetchone()


@app.route("/admin/users")
def admin_users():
    """Display and search all registered LU-TODO users.

    Search fields may be used individually or in any combination:
    - email;
    - first name;
    - last name;
    - position.

    Optional role and status filters are also provided.
    """

    access_response = admin_user_access_required()

    if access_response is not None:
        return access_response

    email = request.args.get(
        "email",
        "",
    ).strip()

    first_name = request.args.get(
        "first_name",
        "",
    ).strip()

    last_name = request.args.get(
        "last_name",
        "",
    ).strip()

    position = request.args.get(
        "position",
        "",
    ).strip()

    role = request.args.get(
        "role",
        "",
    ).strip().lower()

    status = request.args.get(
        "status",
        "",
    ).strip().lower()

    # Ignore invalid filter values rather than passing them to PostgreSQL.
    if role not in VALID_USER_ROLES:
        role = ""

    if status not in VALID_USER_STATUSES:
        status = ""

    with db.get_cursor() as cursor:
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
                u.status,

                (
                    SELECT COUNT(*)
                    FROM projects p
                    WHERE p.owner_id = u.user_id
                ) AS owned_project_count,

                (
                    SELECT COUNT(*)
                    FROM project_members pm
                    WHERE pm.user_id = u.user_id
                ) AS shared_project_count,

                (
                    SELECT COUNT(*)
                    FROM tasks t

                    JOIN projects p
                        ON p.project_id = t.project_id

                    WHERE p.owner_id = u.user_id
                ) AS owned_task_count

            FROM users u

            WHERE
                (
                    %s = ''
                    OR u.email ILIKE '%%' || %s || '%%'
                )

                AND (
                    %s = ''
                    OR u.first_name ILIKE '%%' || %s || '%%'
                )

                AND (
                    %s = ''
                    OR u.last_name ILIKE '%%' || %s || '%%'
                )

                AND (
                    %s = ''
                    OR u.position ILIKE '%%' || %s || '%%'
                )

                AND (
                    %s = ''
                    OR u.user_role::text = %s
                )

                AND (
                    %s = ''
                    OR u.status::text = %s
                )

            ORDER BY
                CASE u.user_role
                    WHEN 'admin' THEN 1
                    WHEN 'staff' THEN 2
                    WHEN 'student' THEN 3
                    ELSE 4
                END,
                LOWER(u.last_name),
                LOWER(u.first_name),
                LOWER(u.email);
            """,
            (
                email,
                email,
                first_name,
                first_name,
                last_name,
                last_name,
                position,
                position,
                role,
                role,
                status,
                status,
            ),
        )

        users = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_user_count,

                COUNT(*) FILTER (
                    WHERE user_role = 'student'
                ) AS student_count,

                COUNT(*) FILTER (
                    WHERE user_role = 'staff'
                ) AS staff_count,

                COUNT(*) FILTER (
                    WHERE user_role = 'admin'
                ) AS admin_count,

                COUNT(*) FILTER (
                    WHERE status = 'active'
                ) AS active_count,

                COUNT(*) FILTER (
                    WHERE status = 'inactive'
                ) AS inactive_count

            FROM users;
            """
        )

        statistics = cursor.fetchone()

    filters = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "position": position,
        "role": role,
        "status": status,
    }

    return render_template(
        "admin_users.html",
        users=users,
        statistics=statistics,
        filters=filters,
        current_admin_id=session["user_id"],
    )


@app.route("/admin/users/<int:user_id>")
def admin_user_profile(user_id):
    """Display the profile and account information of any user."""

    access_response = admin_user_access_required()

    if access_response is not None:
        return access_response

    managed_user = get_managed_user(user_id)

    if managed_user is None:
        flash(
            "The requested user account could not be found.",
            "danger",
        )
        return redirect(url_for("admin_users"))

    return render_template(
        "admin_user_profile.html",
        managed_user=managed_user,
        current_admin_id=session["user_id"],
    )


@app.route(
    "/admin/users/<int:user_id>/role",
    methods=["POST"],
)
def admin_change_user_role(user_id):
    """Promote staff to admin or demote another admin to staff.

    Student roles are permanent and cannot be converted to staff/admin.
    Staff/admin accounts cannot be converted to student.
    The logged-in admin cannot change their own role.
    """

    access_response = admin_user_access_required()

    if access_response is not None:
        return access_response

    current_admin_id = session["user_id"]

    if user_id == current_admin_id:
        flash(
            "You cannot change your own administrator role.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_user_profile",
                user_id=user_id,
            )
        )

    requested_role = request.form.get(
        "user_role",
        "",
    ).strip().lower()

    if requested_role not in {"staff", "admin"}:
        flash(
            "A staff or admin account may only be assigned "
            "the staff or admin role.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_user_profile",
                user_id=user_id,
            )
        )

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                user_id,
                email,
                first_name,
                last_name,
                user_role
            FROM users
            WHERE user_id = %s;
            """,
            (user_id,),
        )

        target_user = cursor.fetchone()

        if target_user is None:
            flash(
                "The requested user account could not be found.",
                "danger",
            )
            return redirect(url_for("admin_users"))

        if target_user["user_role"] == "student":
            flash(
                "Student roles are permanent and cannot be changed "
                "to staff or administrator.",
                "danger",
            )
            return redirect(
                url_for(
                    "admin_user_profile",
                    user_id=user_id,
                )
            )

        if target_user["user_role"] == requested_role:
            flash(
                f'This user already has the "{requested_role}" role.',
                "warning",
            )
            return redirect(
                url_for(
                    "admin_user_profile",
                    user_id=user_id,
                )
            )

        cursor.execute(
            """
            UPDATE users
            SET user_role = %s
            WHERE
                user_id = %s
                AND user_role IN ('staff', 'admin');
            """,
            (
                requested_role,
                user_id,
            ),
        )

    action_description = (
        "promoted to administrator"
        if requested_role == "admin"
        else "changed to staff"
    )

    flash(
        f'{target_user["first_name"]} '
        f'{target_user["last_name"]} was '
        f"{action_description}.",
        "success",
    )

    return redirect(
        url_for(
            "admin_user_profile",
            user_id=user_id,
        )
    )


@app.route(
    "/admin/users/<int:user_id>/status",
    methods=["POST"],
)
def admin_change_user_status(user_id):
    """Activate or deactivate another user account.

    The logged-in administrator cannot deactivate their own account.
    """

    access_response = admin_user_access_required()

    if access_response is not None:
        return access_response

    current_admin_id = session["user_id"]

    if user_id == current_admin_id:
        flash(
            "You cannot change the status of your own account.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_user_profile",
                user_id=user_id,
            )
        )

    requested_status = request.form.get(
        "status",
        "",
    ).strip().lower()

    if requested_status not in VALID_USER_STATUSES:
        flash(
            "Select a valid account status.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_user_profile",
                user_id=user_id,
            )
        )

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                user_id,
                first_name,
                last_name,
                status
            FROM users
            WHERE user_id = %s;
            """,
            (user_id,),
        )

        target_user = cursor.fetchone()

        if target_user is None:
            flash(
                "The requested user account could not be found.",
                "danger",
            )
            return redirect(url_for("admin_users"))

        if target_user["status"] == requested_status:
            flash(
                f'This account is already "{requested_status}".',
                "warning",
            )
            return redirect(
                url_for(
                    "admin_user_profile",
                    user_id=user_id,
                )
            )

        cursor.execute(
            """
            UPDATE users
            SET status = %s
            WHERE user_id = %s;
            """,
            (
                requested_status,
                user_id,
            ),
        )

    flash(
        f'{target_user["first_name"]} '
        f'{target_user["last_name"]} was marked '
        f'{requested_status}.',
        "success",
    )

    return redirect(
        url_for(
            "admin_user_profile",
            user_id=user_id,
        )
    )


@app.route(
    "/admin/users/<int:user_id>/delete",
    methods=["POST"],
)
def admin_delete_user(user_id):
    """Delete another user and their related data.

    Database cascading rules remove:
    - every project owned by the user;
    - all tasks belonging to those projects;
    - all memberships linked to the user;
    - all memberships linked to the deleted projects.

    The logged-in administrator cannot delete themselves.
    """

    access_response = admin_user_access_required()

    if access_response is not None:
        return access_response

    current_admin_id = session["user_id"]

    if user_id == current_admin_id:
        flash(
            "You cannot delete your own administrator account.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_user_profile",
                user_id=user_id,
            )
        )

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                user_id,
                email,
                first_name,
                last_name,
                user_role
            FROM users
            WHERE user_id = %s;
            """,
            (user_id,),
        )

        target_user = cursor.fetchone()

        if target_user is None:
            flash(
                "The requested user account could not be found.",
                "danger",
            )
            return redirect(url_for("admin_users"))

        cursor.execute(
            """
            DELETE FROM users
            WHERE
                user_id = %s
                AND user_id <> %s
            RETURNING user_id;
            """,
            (
                user_id,
                current_admin_id,
            ),
        )

        deleted_user = cursor.fetchone()

    if deleted_user is None:
        flash(
            "The user account could not be deleted.",
            "danger",
        )
    else:
        flash(
            f'{target_user["first_name"]} '
            f'{target_user["last_name"]} '
            f'({target_user["email"]}) was deleted. '
            "Their owned projects, tasks, and memberships "
            "were also removed.",
            "success",
        )

    return redirect(url_for("admin_users"))