"""User authentication and account routes for LU-TODO.

This module provides:
- Email-based login
- Student and staff registration
- Logout
- Profile viewing
- Role-specific homepage redirects
"""

import os
import re
from functools import wraps

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

from loginapp import app
from loginapp import db


# Flask-Bcrypt is used to hash and verify passwords.
flask_bcrypt = Bcrypt(app)


# Profile-picture settings.
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

# Create the upload directory if it does not already exist.
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)

app.config["PROFILE_UPLOAD_FOLDER"] = PROFILE_UPLOAD_FOLDER

# Maximum uploaded file size: 5 MB.
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def login_required(route_function):
    """Require a user to be logged in before accessing a route."""

    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return decorated_function


def allowed_profile_picture(filename):
    """Check whether a profile-picture filename has an allowed extension."""

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def determine_user_role(email):
    """Determine a new user's role from their Lincoln email domain.

    Students:
        @lincolnuni.ac.nz

    Staff:
        @lincoln.ac.nz

    Admin accounts cannot be created through public registration.
    """

    email = email.strip().lower()

    if email.endswith("@lincolnuni.ac.nz"):
        return "student"

    if email.endswith("@lincoln.ac.nz"):
        return "staff"

    return None


def validate_password(password):
    """Validate a password against the LU-TODO password requirements.

    Passwords must contain:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """

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


def user_home_url():
    """Return the homepage URL for the logged-in user's role."""

    if "user_id" not in session:
        return url_for("login")

    role = session.get("user_role")

    if role == "student":
        return url_for("student_home")

    if role == "staff":
        return url_for("staff_home")

    if role == "admin":
        return url_for("admin_home")

    # Invalid role: clear the session through logout.
    return url_for("logout")


@app.route("/")
def root():
    """Redirect guests to login and users to their homepage."""

    return redirect(user_home_url())


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user with their Lincoln email and password."""

    # Already logged-in users do not need to see the login form.
    if "user_id" in session:
        return redirect(user_home_url())

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Check that both fields were submitted.
        if not email or not password:
            flash(
                "Please enter your email address and password.",
                "danger",
            )

            return render_template(
                "login.html",
                email=email,
            )

        # Find the account using the supplied email.
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    user_id,
                    email,
                    first_name,
                    last_name,
                    password_hash,
                    user_role,
                    status
                FROM users
                WHERE LOWER(email) = LOWER(%s);
                """,
                (email,),
            )

            account = cursor.fetchone()

        # Temporary server-log message for testing.
        print("LOGIN DEBUG - ACCOUNT FOUND:", account is not None)

        if account is None:
            return render_template(
                "login.html",
                email=email,
                email_invalid=True,
            )

        # Inactive users must not be allowed to log in.
        if account["status"] != "active":
            flash(
                "Your account is inactive. "
                "Please contact an administrator.",
                "danger",
            )

            return render_template(
                "login.html",
                email=email,
            )

        # Compare the submitted password with the stored bcrypt hash.
        password_is_correct = flask_bcrypt.check_password_hash(
            account["password_hash"],
            password,
        )

        # Temporary server-log message for testing.
        print(
            "LOGIN DEBUG - PASSWORD CORRECT:",
            password_is_correct,
        )

        if not password_is_correct:
            return render_template(
                "login.html",
                email=email,
                password_invalid=True,
            )

        # Clear any previous session before storing the new login details.
        session.clear()

        session["loggedin"] = True
        session["user_id"] = account["user_id"]
        session["email"] = account["email"]
        session["first_name"] = account["first_name"]
        session["last_name"] = account["last_name"]
        session["user_role"] = account["user_role"]

        flash(
            f"Welcome back, {account['first_name']}!",
            "success",
        )

        # Temporary test redirect.
        # Once login is confirmed working, replace this with:
        # return redirect(user_home_url())
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register a new LU-TODO student or staff account."""

    if "user_id" in session:
        return redirect(user_home_url())

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
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
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            "",
        )
        profile_picture_file = request.files.get(
            "profile_picture"
        )

        errors = {}

        # Validate first name.
        if not first_name:
            errors["first_name_error"] = (
                "First name is required."
            )
        elif len(first_name) > 100:
            errors["first_name_error"] = (
                "First name cannot exceed 100 characters."
            )

        # Validate last name.
        if not last_name:
            errors["last_name_error"] = (
                "Last name is required."
            )
        elif len(last_name) > 100:
            errors["last_name_error"] = (
                "Last name cannot exceed 100 characters."
            )

        # Validate position.
        if not position:
            errors["position_error"] = (
                "Position is required."
            )
        elif len(position) > 150:
            errors["position_error"] = (
                "Position cannot exceed 150 characters."
            )

        # Validate email and determine the new user's role.
        user_role = None

        if not email:
            errors["email_error"] = (
                "Email address is required."
            )
        elif len(email) > 254:
            errors["email_error"] = (
                "Email address cannot exceed 254 characters."
            )
        elif not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email,
        ):
            errors["email_error"] = (
                "Enter a valid email address."
            )
        else:
            user_role = determine_user_role(email)

            if user_role is None:
                errors["email_error"] = (
                    "Use an @lincolnuni.ac.nz student email "
                    "or an @lincoln.ac.nz staff email."
                )

        # Validate password.
        password_error = validate_password(password)

        if password_error:
            errors["password_error"] = password_error

        # Validate password confirmation.
        if not confirm_password:
            errors["confirm_password_error"] = (
                "Please enter the password again."
            )
        elif password != confirm_password:
            errors["confirm_password_error"] = (
                "The two passwords do not match."
            )

        # Check that the email is unique.
        if email and "email_error" not in errors:
            with db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE LOWER(email) = LOWER(%s);
                    """,
                    (email,),
                )

                existing_account = cursor.fetchone()

            if existing_account is not None:
                errors["email_error"] = (
                    "An account already exists with "
                    "this email address."
                )

        # Validate optional profile picture.
        if (
            profile_picture_file
            and profile_picture_file.filename
        ):
            if not allowed_profile_picture(
                profile_picture_file.filename
            ):
                errors["profile_picture_error"] = (
                    "Profile picture must be PNG, JPG, "
                    "JPEG, GIF, or WEBP."
                )

        # Return the user to the form when validation fails.
        if errors:
            return render_template(
                "signup.html",
                email=email,
                first_name=first_name,
                last_name=last_name,
                position=position,
                **errors,
            )

        profile_picture_filename = None

        # Save optional profile picture.
        if (
            profile_picture_file
            and profile_picture_file.filename
        ):
            original_filename = secure_filename(
                profile_picture_file.filename
            )

            file_extension = original_filename.rsplit(
                ".",
                1,
            )[1].lower()

            email_prefix = re.sub(
                r"[^A-Za-z0-9_-]",
                "_",
                email.split("@")[0],
            )

            random_part = os.urandom(6).hex()

            profile_picture_filename = (
                f"{email_prefix}_{random_part}."
                f"{file_extension}"
            )

            profile_picture_path = os.path.join(
                app.config["PROFILE_UPLOAD_FOLDER"],
                profile_picture_filename,
            )

            profile_picture_file.save(
                profile_picture_path
            )

        # Hash the password before inserting the account.
        password_hash = (
            flask_bcrypt.generate_password_hash(
                password
            ).decode("utf-8")
        )

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    email,
                    first_name,
                    last_name,
                    position,
                    profile_picture,
                    password_hash,
                    user_role,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'active'
                );
                """,
                (
                    email,
                    first_name,
                    last_name,
                    position,
                    profile_picture_filename,
                    password_hash,
                    user_role,
                ),
            )

        flash(
            "Your LU-TODO account has been created. "
            "You can now log in.",
            "success",
        )

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/profile")
@login_required
def profile():
    """Display the currently logged-in user's profile."""

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

        user_profile = cursor.fetchone()

    if user_profile is None:
        session.clear()

        flash(
            "Your account could not be found. "
            "Please log in again.",
            "danger",
        )

        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        profile=user_profile,
    )


@app.route("/logout")
def logout():
    """Clear the session and return to the login page."""

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success",
    )

    return redirect(url_for("login"))