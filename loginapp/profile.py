"""Profile management routes for LU-TODO."""

import os
import re

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from loginapp import app, db
from loginapp.user import login_required


flask_bcrypt = Bcrypt(app)

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
}

PROFILE_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "profile_pictures",
)

os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)

app.config["PROFILE_UPLOAD_FOLDER"] = PROFILE_UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def allowed_profile_picture(filename):
    """Check whether an uploaded image has an allowed extension."""

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def validate_new_password(password):
    """Validate a new password."""

    if len(password) < 8:
        return "Password must contain at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"\d", password):
        return "Password must contain at least one number."

    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character."

    return None


def get_current_profile():
    """Get the currently logged-in user's profile."""

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                user_id,
                email,
                first_name,
                last_name,
                position,
                profile_picture,
                user_role,
                status
            FROM users
            WHERE user_id = %s;
            """,
            (session["user_id"],),
        )

        return cursor.fetchone()


def delete_profile_picture(filename):
    """Delete a profile-picture file if it exists."""

    if not filename:
        return

    safe_filename = os.path.basename(filename)

    file_path = os.path.join(
        app.config["PROFILE_UPLOAD_FOLDER"],
        safe_filename,
    )

    if os.path.isfile(file_path):
        os.remove(file_path)


@app.route("/profile")
@login_required
def profile():
    """Show the current user's profile."""

    user_profile = get_current_profile()

    if user_profile is None:
        session.clear()

        flash(
            "Your account could not be found. Please log in again.",
            "danger",
        )

        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        profile=user_profile,
    )


@app.route("/profile/edit", methods=["POST"])
@login_required
def edit_profile():
    """Update name and position only.

    The email address cannot be changed.
    """

    first_name = request.form.get(
        "first_name",
        "",
    ).strip()

    last_name = request.form.get(
        "last_name",
        "",
    ).strip()

    position = request.form.get(
        "position",
        "",
    ).strip()

    errors = []

    if not first_name:
        errors.append("First name is required.")
    elif len(first_name) > 100:
        errors.append(
            "First name cannot exceed 100 characters."
        )

    if not last_name:
        errors.append("Last name is required.")
    elif len(last_name) > 100:
        errors.append(
            "Last name cannot exceed 100 characters."
        )

    if not position:
        errors.append("Position is required.")
    elif len(position) > 150:
        errors.append(
            "Position cannot exceed 150 characters."
        )

    if errors:
        for error in errors:
            flash(error, "danger")

        return redirect(url_for("profile"))

    # Email is intentionally not included in this query.
    with db.get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE users
            SET
                first_name = %s,
                last_name = %s,
                position = %s
            WHERE user_id = %s;
            """,
            (
                first_name,
                last_name,
                position,
                session["user_id"],
            ),
        )

    session["first_name"] = first_name
    session["last_name"] = last_name

    flash(
        "Your profile has been updated successfully.",
        "success",
    )

    return redirect(url_for("profile"))


@app.route("/profile/picture", methods=["POST"])
@login_required
def update_profile_picture():
    """Upload or replace the current user's profile picture."""

    uploaded_file = request.files.get("profile_picture")

    if uploaded_file is None or not uploaded_file.filename:
        flash(
            "Please choose an image to upload.",
            "danger",
        )

        return redirect(url_for("profile"))

    if not allowed_profile_picture(uploaded_file.filename):
        flash(
            "Profile picture must be PNG, JPG, JPEG, GIF or WEBP.",
            "danger",
        )

        return redirect(url_for("profile"))

    current_profile = get_current_profile()

    if current_profile is None:
        session.clear()
        flash("Your account could not be found.", "danger")
        return redirect(url_for("login"))

    original_filename = secure_filename(
        uploaded_file.filename
    )

    extension = original_filename.rsplit(
        ".",
        1,
    )[1].lower()

    new_filename = (
        f"user_{session['user_id']}_"
        f"{os.urandom(8).hex()}.{extension}"
    )

    new_file_path = os.path.join(
        app.config["PROFILE_UPLOAD_FOLDER"],
        new_filename,
    )

    uploaded_file.save(new_file_path)

    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET profile_picture = %s
                WHERE user_id = %s;
                """,
                (
                    new_filename,
                    session["user_id"],
                ),
            )

    except Exception:
        if os.path.isfile(new_file_path):
            os.remove(new_file_path)

        raise

    old_filename = current_profile["profile_picture"]

    if old_filename and old_filename != new_filename:
        delete_profile_picture(old_filename)

    flash(
        "Your profile picture has been updated.",
        "success",
    )

    return redirect(url_for("profile"))


@app.route("/profile/picture/remove", methods=["POST"])
@login_required
def remove_profile_picture():
    """Remove the current user's profile picture."""

    current_profile = get_current_profile()

    if current_profile is None:
        session.clear()
        flash("Your account could not be found.", "danger")
        return redirect(url_for("login"))

    current_filename = current_profile["profile_picture"]

    if not current_filename:
        flash(
            "You do not currently have a profile picture.",
            "warning",
        )

        return redirect(url_for("profile"))

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE users
            SET profile_picture = NULL
            WHERE user_id = %s;
            """,
            (session["user_id"],),
        )

    delete_profile_picture(current_filename)

    flash(
        "Your profile picture has been removed.",
        "success",
    )

    return redirect(url_for("profile"))


@app.route("/profile/password", methods=["POST"])
@login_required
def change_password():
    """Change the current user's password."""

    current_password = request.form.get(
        "current_password",
        "",
    )

    new_password = request.form.get(
        "new_password",
        "",
    )

    confirm_password = request.form.get(
        "confirm_password",
        "",
    )

    if not current_password:
        flash("Enter your current password.", "danger")
        return redirect(url_for("profile"))

    if not new_password:
        flash("Enter a new password.", "danger")
        return redirect(url_for("profile"))

    if new_password != confirm_password:
        flash(
            "The new passwords do not match.",
            "danger",
        )

        return redirect(url_for("profile"))

    password_error = validate_new_password(new_password)

    if password_error:
        flash(password_error, "danger")
        return redirect(url_for("profile"))

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT password_hash
            FROM users
            WHERE user_id = %s;
            """,
            (session["user_id"],),
        )

        account = cursor.fetchone()

    if account is None:
        session.clear()
        flash("Your account could not be found.", "danger")
        return redirect(url_for("login"))

    if not flask_bcrypt.check_password_hash(
        account["password_hash"],
        current_password,
    ):
        flash(
            "Your current password is incorrect.",
            "danger",
        )

        return redirect(url_for("profile"))

    if flask_bcrypt.check_password_hash(
        account["password_hash"],
        new_password,
    ):
        flash(
            "Your new password must be different "
            "from your current password.",
            "danger",
        )

        return redirect(url_for("profile"))

    new_password_hash = (
        flask_bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")
    )

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE user_id = %s;
            """,
            (
                new_password_hash,
                session["user_id"],
            ),
        )

    flash(
        "Your password has been changed successfully.",
        "success",
    )

    return redirect(url_for("profile"))