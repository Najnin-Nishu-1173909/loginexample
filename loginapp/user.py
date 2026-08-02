"""Authentication and registration routes for LU-TODO."""

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


flask_bcrypt = Bcrypt(app)


# Profile-picture settings used during registration.
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

# Maximum uploaded file size: 5 MB.
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def login_required(route_function):
    """Require a user to be logged in before accessing a route."""

    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash(
                "Please log in to continue.",
                "warning",
            )

            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return decorated_function


def allowed_profile_picture(filename):
    """Return True if the uploaded image has an allowed extension."""

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def determine_user_role(email):
    """Determine a user's role from their Lincoln email address.

    Student:
        @lincolnuni.ac.nz

    Staff:
        @lincoln.ac.nz

    Admin accounts cannot be created using public registration.
    """

    email = email.strip().lower()

    if email.endswith("@lincolnuni.ac.nz"):
        return "student"

    if email.endswith("@lincoln.ac.nz"):
        return "staff"

    return None


def validate_password(password):
    """Validate a password against LU-TODO requirements."""

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
    """Return the appropriate homepage for the logged-in user."""

    if "user_id" not in session:
        return url_for("login")

    user_role = session.get("user_role")

    if user_role == "student":
        return url_for("student_home")

    if user_role == "staff":
        return url_for("staff_home")

    if user_role == "admin":
        return url_for("admin_home")

    # Invalid session role.
    return url_for("logout")


@app.route("/")
def root():
    """Redirect visitors to login or their role-specific dashboard."""

    return redirect(user_home_url())


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate users using their Lincoln email and password."""

    if "user_id" in session:
        return redirect(user_home_url())

    if request.method == "POST":
        email = request.form.get(
            "email",
            "",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        if not email or not password:
            flash(
                "Please enter your email address and password.",
                "danger",
            )

            return render_template(
                "login.html",
                email=email,
            )

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

        if account is None:
            return render_template(
                "login.html",
                email=email,
                email_invalid=True,
            )

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

        password_is_correct = (
            flask_bcrypt.check_password_hash(
                account["password_hash"],
                password,
            )
        )

        if not password_is_correct:
            return render_template(
                "login.html",
                email=email,
                password_invalid=True,
            )

        # Clear any previous session data.
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

        return redirect(user_home_url())

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register a new student or staff user."""

    if "user_id" in session:
        return redirect(user_home_url())

    if request.method == "POST":
        email = request.form.get(
            "email",
            "",
        ).strip().lower()

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

        password = request.form.get(
            "password",
            "",
        )

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

        # Validate email and determine role.
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

        # Confirm password.
        if not confirm_password:
            errors["confirm_password_error"] = (
                "Please enter the password again."
            )

        elif password != confirm_password:
            errors["confirm_password_error"] = (
                "The two passwords do not match."
            )

        # Check email uniqueness.
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
                    "JPEG, GIF or WEBP."
                )

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

            random_part = os.urandom(8).hex()

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

        password_hash = (
            flask_bcrypt.generate_password_hash(
                password
            ).decode("utf-8")
        )

        try:
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

        except Exception:
            # Remove the uploaded image if registration fails.
            if profile_picture_filename:
                uploaded_file_path = os.path.join(
                    app.config["PROFILE_UPLOAD_FOLDER"],
                    profile_picture_filename,
                )

                if os.path.isfile(uploaded_file_path):
                    os.remove(uploaded_file_path)

            raise

        flash(
            "Your LU-TODO account has been created. "
            "You can now log in.",
            "success",
        )

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    """Log the current user out."""

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success",
    )

    return redirect(url_for("login"))