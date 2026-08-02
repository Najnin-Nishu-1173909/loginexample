"""Student routes for LU-TODO."""

from flask import redirect, render_template, session, url_for

from loginapp import app


@app.route("/student/home")
def student_home():
    """Display the homepage for a logged-in student."""

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "student":
        return render_template("access_denied.html"), 403

    return render_template("student_home.html")