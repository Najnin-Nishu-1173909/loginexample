@app.route("/profile/edit", methods=["POST"])
@login_required
def edit_profile():
    """Update first name, last name and position only.

    Email address cannot be changed.
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

    # IMPORTANT:
    # Do NOT read request.form["email"].
    # Email addresses are permanent and cannot be changed.

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