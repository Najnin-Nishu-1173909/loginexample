# LU-TODO

**A secure, role-based project and task management web application for Lincoln University**

LU-TODO is a custom “in-house” to-do list system developed for the COMP639 Individual Assignment at Lincoln University. It allows students and staff to organise individual work, supports project collaboration for staff and administrators, and provides administrators with system-wide project and user-management tools.

The application is implemented with **Python, Flask, PostgreSQL, Bootstrap 5, JavaScript, HTML, and CSS** and is deployed on **PythonAnywhere**.

---

## Project information

| Item | Details |
|---|---|
| Project | LU-TODO |
| Course | COMP639 – Studio Project |
| Assessment | Individual Assignment, Semester 2, 2026 |
| Developer | Najnin Sultana Nishu |
| Student ID | 1173909 |
| Production platform | PythonAnywhere |
| Database | PostgreSQL |
| Repository visibility | Private |

### Live application

`https://najninsultana.pythonanywhere.com`

### GitHub repository

`https://github.com/Najnin-Nishu-1173909/LU-TODO`

> The repository is private. The GitHub user `lincolnmac` must be added as a collaborator for assessment access.

---

## Purpose and scope

Lincoln University requires a task-management platform that gives the university control over its data and can be extended with institution-specific features in the future. LU-TODO provides the first prototype of that platform.

The system supports three user roles:

- **Student:** creates and manages private personal projects and tasks.
- **Staff:** creates private or shared projects, manages tasks, and collaborates with students, staff, and administrators.
- **Administrator:** has the normal project features available to staff and can also administer shared projects and user accounts across the system.

The application deliberately separates normal project access from administrative access. An administrator can administer shared projects at a system level, but unrelated private projects are not shown in the system shared-project administration area.

---

## Main features

### Account and security

- Registration using a Lincoln University email address.
- Role assignment based on the user’s email domain.
- One login process for students, staff, and administrators.
- Password hashing using Flask-Bcrypt.
- Session-based authentication.
- Role-based route protection.
- Active and inactive account status.
- Logout and session clearing.
- Server-side validation and user-friendly error messages.
- Access-denied responses for unauthorised role access.

### User profile

All authenticated users can:

- View their profile.
- Edit first name, last name, and position.
- View their email address without being able to edit it.
- Add, replace, or remove a profile picture.
- See a placeholder when no profile picture has been uploaded.
- Change their password.

Uploaded images are stored under:

```text
loginapp/static/profile_pictures/
```

The interface displays profile images in a fixed circular frame with `object-fit: cover`, so different image sizes and shapes display consistently.

### Student functionality

Students can:

- View their dashboard.
- Create private projects.
- Edit and delete projects they own.
- View task statistics for their projects.
- Create, edit, complete, reopen, and delete tasks.
- Set task priority and an optional due date.
- See overdue tasks clearly identified.
- Not share projects they own.

### Staff functionality

Staff can:

- Create, edit, and delete projects they own.
- Create private projects or share owned projects.
- Add multiple students, staff members, or administrators as project members.
- View and remove members from projects they own.
- View owned projects and projects shared directly with them.
- Create, edit, complete, reopen, and delete tasks in accessible projects.
- See project progress, member totals, task totals, and overdue task counts.
- Not rename, delete, or manage members for a project they do not own.

### Administrator functionality

Administrators can:

- Use all normal project, task, and sharing functions available to staff.
- View a dashboard containing system and personal statistics.
- View and manage projects they own.
- View projects shared directly with them.
- View every project that is shared with at least one user.
- Search system-wide shared projects.
- View project owners, task statistics, and member totals.
- Transfer ownership of a shared project to an eligible **staff** or **administrator** account.
- Prevent students from becoming project owners through administrative transfer.
- Delete shared projects and their related tasks and memberships.
- View and search all registered users.
- Search by email, first name, last name, position, role, and status.
- View an individual user’s profile and account statistics.
- Promote staff users to administrator.
- Demote another administrator to staff.
- Activate or deactivate another user account.
- Delete another user account and its dependent data.
- Never change their own role, deactivate themselves, or delete their own account.
- Never convert a student account to staff/admin or a staff/admin account to student.

---

## Technology stack

| Technology | Purpose |
|---|---|
| Python 3 | Application logic |
| Flask | Web framework and routing |
| PostgreSQL | Relational data storage |
| Psycopg 2 | PostgreSQL database connection and queries |
| Flask-Bcrypt | Password hashing and verification |
| Bootstrap 5 | Responsive layout and interface components |
| Bootstrap Icons | Interface icons |
| HTML5 / Jinja | Server-rendered templates |
| CSS | Bootstrap colour overrides and presentation styling |
| JavaScript | Client-side filtering and selection interactions |
| Git / GitHub | Version control and submission repository |
| PythonAnywhere | Production hosting and PostgreSQL environment |

The project does not use SQLAlchemy, React, or another unapproved framework.

---

## Application architecture

The project uses a modular Flask structure. Route logic is separated by role and feature.

```text
LU-TODO/
├── loginapp/
│   ├── __init__.py
│   ├── admin.py
│   ├── admin_projects.py
│   ├── admin_sharing.py
│   ├── admin_tasks.py
│   ├── admin_users.py
│   ├── connect.py
│   ├── db.py
│   ├── profile.py
│   ├── staff.py
│   ├── staff_sharing.py
│   ├── staff_tasks.py
│   ├── student.py
│   ├── student_tasks.py
│   ├── user.py
│   ├── static/
│   │   └── profile_pictures/
│   └── templates/
│       ├── access_denied.html
│       ├── admin_home.html
│       ├── admin_members.html
│       ├── admin_project.html
│       ├── admin_system_projects.html
│       ├── admin_user_profile.html
│       ├── admin_users.html
│       ├── home.html
│       ├── login.html
│       ├── profile.html
│       ├── signup.html
│       ├── staff_home.html
│       ├── staff_members.html
│       ├── staff_project.html
│       ├── student_home.html
│       ├── student_project.html
│       └── userbase.html
├── .gitignore
├── create_database.sql
├── populate_database.sql
├── password_hash_generator.py
├── README.md
├── requirements.txt
└── run.py
```

`connect.py` contains environment-specific database credentials and is excluded from Git through `.gitignore`.

---

## Database design

The PostgreSQL database stores users, projects, tasks, and project memberships.

### `users`

Stores the user ID, Lincoln email address, first and last name, position, profile-picture filename, password hash, user role, and account status.

### `projects`

Stores the project ID, owner, name, and description. Each project has one owner.

### `tasks`

Stores the task ID, parent project, name, description, priority, due date, and completion status.

### `project_members`

Represents the many-to-many relationship between users and shared projects. The owner is not inserted as a project member; ownership and membership are separate access relationships.

### Referential behaviour

- Deleting a project removes its tasks and memberships.
- Deleting a user removes projects owned by that user and dependent tasks and memberships.
- Removing a project member removes only that membership relationship.

---

## Required repository files

The repository includes:

- Python application modules.
- Jinja/HTML templates.
- Static assets required by the application.
- `requirements.txt`.
- `create_database.sql`.
- `populate_database.sql`.
- `README.md`.
- `.gitignore`.

The following should not be committed:

```text
venv/
__pycache__/
*.pyc
loginapp/connect.py
```

---

# Local setup

## Prerequisites

- Python 3.11 or later
- PostgreSQL
- Git
- Visual Studio Code or another editor

Check the installed tools:

```powershell
python --version
git --version
```

## 1. Clone the repository

```powershell
git clone https://github.com/Najnin-Nishu-1173909/LU-TODO.git
cd LU-TODO
```

Because the repository is private, the user cloning it must have access.

## 2. Create and activate a virtual environment

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux or macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Create the PostgreSQL database

Create an empty database, then run:

```bash
psql -U YOUR_DATABASE_USER -d YOUR_DATABASE_NAME -f create_database.sql
```

Populate it:

```bash
psql -U YOUR_DATABASE_USER -d YOUR_DATABASE_NAME -f populate_database.sql
```

Run `create_database.sql` before `populate_database.sql`.

## 5. Create `loginapp/connect.py`

```python
"""Local PostgreSQL connection settings for LU-TODO."""

dbuser = "YOUR_DATABASE_USERNAME"
dbpass = "YOUR_DATABASE_PASSWORD"
dbhost = "localhost"
dbname = "YOUR_DATABASE_NAME"
dbport = 5432
```

Do not commit this file.

## 6. Configure the secret key

The Flask app requires a secret key for sessions. A production value should be long and unpredictable. It may be loaded from an environment variable:

```python
import os

app.secret_key = os.environ.get(
    "LU_TODO_SECRET_KEY",
    "development-only-fallback"
)
```

Windows PowerShell:

```powershell
$env:LU_TODO_SECRET_KEY="replace-with-a-long-random-value"
```

Linux:

```bash
export LU_TODO_SECRET_KEY="replace-with-a-long-random-value"
```

## 7. Create the profile-picture directory

Windows:

```powershell
New-Item -ItemType Directory -Force loginapp\static\profile_pictures
```

Linux/macOS:

```bash
mkdir -p loginapp/static/profile_pictures
```

## 8. Run locally

```powershell
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# PythonAnywhere deployment

## 1. Add the teacher

In PythonAnywhere:

```text
Account → Education → Your teacher
```

Add:

```text
lincolnmac
```

## 2. Clone the private repository

```bash
cd ~
git clone https://github.com/Najnin-Nishu-1173909/LU-TODO.git
cd LU-TODO
```

Authenticate using the GitHub method configured for the account.

## 3. Create the virtual environment

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Use the Python version selected for the PythonAnywhere web app.

## 4. Configure PostgreSQL

Create `loginapp/connect.py` using the exact PostgreSQL credentials supplied for the assignment:

```python
"""PythonAnywhere PostgreSQL connection settings."""

dbuser = "YOUR_PYTHONANYWHERE_DATABASE_USERNAME"
dbpass = "YOUR_PYTHONANYWHERE_DATABASE_PASSWORD"
dbhost = "YOUR_PYTHONANYWHERE_POSTGRES_HOST"
dbname = "YOUR_PYTHONANYWHERE_DATABASE_NAME"
dbport = YOUR_PYTHONANYWHERE_DATABASE_PORT
```

## 5. Create and populate the hosted database

```bash
psql \
  --host=YOUR_POSTGRES_HOST \
  --port=YOUR_POSTGRES_PORT \
  --username=YOUR_DATABASE_USERNAME \
  --dbname=YOUR_DATABASE_NAME \
  --file=create_database.sql
```

Then:

```bash
psql \
  --host=YOUR_POSTGRES_HOST \
  --port=YOUR_POSTGRES_PORT \
  --username=YOUR_DATABASE_USERNAME \
  --dbname=YOUR_DATABASE_NAME \
  --file=populate_database.sql
```

## 6. Configure the WSGI file

When the deployment folder is `LU-TODO`:

```python
import sys

project_home = "/home/najninsultana/LU-TODO"

if project_home not in sys.path:
    sys.path.insert(0, project_home)

from loginapp import app as application
```

If the existing PythonAnywhere folder is still named `loginexample`, use:

```python
project_home = "/home/najninsultana/loginexample"
```

The path must match the actual deployment directory.

## 7. Configure the virtual-environment path

In the **Web** tab, set:

```text
/home/najninsultana/LU-TODO/venv
```

or the matching path if the server folder has a different name.

## 8. Static files

If a PythonAnywhere static mapping is configured:

```text
URL:       /static/
Directory: /home/najninsultana/LU-TODO/loginapp/static/
```

## 9. Reload and diagnose

Select **Web → Reload**.

Production URL:

```text
https://najninsultana.pythonanywhere.com
```

Inspect errors:

```bash
tail -60 /var/log/najninsultana.pythonanywhere.com.error.log
```

Test imports:

```bash
python -c "from loginapp import app; print('Application loaded successfully')"
```

Inspect routes:

```bash
python -c "from loginapp import app; print(app.url_map)"
```

---

## Updating PythonAnywhere

From the local project:

```powershell
git status
git add .
git commit -m "Describe the completed change"
git push origin main
```

On PythonAnywhere:

```bash
cd ~/LU-TODO
git pull origin main
```

Then select **Web → Reload**.

Do not modify GitHub or PythonAnywhere after the submission deadline until marks have been released.

---

# User guide

## Registration

1. Select **Register**.
2. Enter a Lincoln email address, first name, last name, position, optional profile picture, password, and password confirmation.
3. Follow the validation hints.
4. Submit the form.
5. Log in through the common login page.

The email domain determines the initial account role.

## Login and logout

1. Enter a registered Lincoln email address and password.
2. Select **Log in**.
3. The application redirects to the appropriate role dashboard.
4. Select **Log out** to end the session.

Inactive accounts cannot log in.

## Profile

1. Select **Profile**.
2. Edit first name, last name, or position.
3. Save changes.
4. Add, replace, or remove the profile picture.
5. Change the password when required.

The email address is visible but read-only.

## Student workflow

1. Create a project from the Student Dashboard.
2. Enter a unique name and optional description.
3. Open the project to add tasks.
4. Set task name, optional description, priority, and optional due date.
5. Edit, complete, reopen, or delete tasks as required.
6. Edit or delete owned projects.

Students cannot share projects they own.

## Staff workflow

1. Create and manage owned projects.
2. Open **Members & Sharing** for an owned project.
3. Search or filter available users.
4. Select one or more users and add them.
5. Remove members when required.
6. Manage tasks in owned or directly shared projects.

Staff cannot rename, delete, or reshare a project they do not own.

## Administrator workflow

### Shared-project administration

1. Open **Shared projects**.
2. Search by project or owner information.
3. Review owner, member, task, and overdue information.
4. Transfer ownership to an eligible staff or administrator.
5. Delete a shared project when required.

Unrelated private projects are excluded, and students cannot become owners through transfer.

### User administration

1. Open **Users**.
2. Search by email, first name, last name, position, role, and status.
3. Open **View and manage account**.
4. Promote staff to administrator or demote another administrator to staff.
5. Activate or deactivate another user.
6. Delete another account when required.

The logged-in administrator cannot change their own role, deactivate themselves, or delete themselves. Student roles cannot be converted.

---

# Security and validation

## Password security

- Plain-text passwords are never stored.
- Flask-Bcrypt generates and checks password hashes.
- Registration requires password confirmation.
- Password constraints are validated server-side.

## Session management

- Authentication data is stored in the Flask session.
- Protected routes require a logged-in user.
- Role checks protect role-specific pages.
- Logout clears the session.

## Authorisation

Server-side checks ensure that:

- Students cannot access staff or admin routes.
- Knowing a project ID does not grant access.
- Member management requires project ownership.
- Normal task access requires ownership or membership.
- System project and user administration require the admin role.
- Admin self-protection rules are enforced in Python and the interface.

## Validation

The application validates:

- Required fields.
- Email domains.
- Password requirements.
- Maximum lengths.
- Role and status values.
- Task priorities.
- Dates.
- Existing projects and users.
- Unique project names per owner.
- Duplicate memberships.
- Ownership-transfer eligibility.

---

# Testing checklist

## Accounts

- [ ] Register valid student and staff accounts.
- [ ] Reject invalid email domains.
- [ ] Reject mismatched or weak passwords.
- [ ] Log in and log out as student, staff, and admin.
- [ ] Confirm inactive accounts cannot log in.

## Profile

- [ ] Edit first name, last name, and position.
- [ ] Confirm email is read-only.
- [ ] Add, replace, and remove a profile picture.
- [ ] Test differently shaped images.
- [ ] Change password and log in again.

## Projects and tasks

- [ ] Create, edit, and delete owned projects.
- [ ] Create tasks with each priority.
- [ ] Test optional due dates.
- [ ] Complete and reopen tasks.
- [ ] Confirm overdue highlighting.
- [ ] Confirm unauthorised URL access is rejected.

## Sharing

- [ ] Add multiple members.
- [ ] Prevent duplicate memberships.
- [ ] Remove a member.
- [ ] Confirm non-owners cannot manage members.
- [ ] Confirm students cannot share owned projects.

## Administrator

- [ ] Confirm private unrelated projects are excluded from system shared projects.
- [ ] Transfer ownership to staff and admin.
- [ ] Confirm students cannot become owners.
- [ ] Delete a shared project and verify dependent data removal.
- [ ] Search users using combined criteria.
- [ ] Promote staff and demote another admin.
- [ ] Activate and deactivate another user.
- [ ] Confirm self-role, self-status, and self-delete protections.
- [ ] Delete another user and verify dependent data removal.

## Responsive interface

- [ ] Test desktop, tablet, and mobile widths.
- [ ] Check navigation collapse.
- [ ] Check form and card layout.
- [ ] Check long emails and descriptions.
- [ ] Check flash and validation messages.

---

# Generative AI acknowledgement

## Tool used

I used **OpenAI ChatGPT** during this assessment.

## Description of use

ChatGPT was used as a development and learning assistant for:

1. **Assessment interpretation**
   - I supplied the COMP639 assignment PDF and asked ChatGPT to identify the requirements for student, staff, and administrator roles.
   - I asked it to compare the current implementation with the brief and identify missing work.

2. **Application planning**
   - I asked for guidance on organising the Flask application into separate role- and feature-specific modules.

3. **Code drafting and refinement**
   - I asked ChatGPT to draft and revise Flask routes, PostgreSQL queries, Jinja templates, Bootstrap interfaces, validation logic, permission checks, project sharing, task management, and administrator functions.
   - I requested complete files for review, integration, and testing.

4. **Debugging**
   - I supplied PythonAnywhere tracebacks, Flask route maps, Git output, screenshots, and code snippets.
   - ChatGPT helped explain missing endpoints, missing templates, circular imports, application-context errors, `BuildError` exceptions, and deployment problems.
   - I executed the suggested diagnostics and verified the actual results.

5. **Git and deployment**
   - I asked for help with staging, committing, pushing, pulling, repository renaming, PythonAnywhere configuration, reloads, and error-log inspection.

6. **Test data**
   - ChatGPT assisted with ideas for realistic user names, roles, positions, projects, tasks, and memberships.
   - Passwords were stored as hashes rather than plain text.

7. **Documentation**
   - I asked ChatGPT to help draft this project-specific README, including setup, deployment, usage, security, testing, architecture, and the GenAI acknowledgement.

## Representative prompts and inputs

```text
Read the assignment PDF carefully and tell me what remains in the student section.
```

```text
Configure the staff dashboard requirements according to the assignment.
```

```text
Give me the full HTML and Python code separately so I can copy, review, and test each file.
```

```text
A student must not be able to edit their email. Update the profile code accordingly.
```

```text
Create admin task-management routes for projects an admin owns or that are shared directly with them.
```

```text
Implement admin project sharing so an admin can add multiple users and remove members only from projects the admin owns.
```

```text
Implement the admin requirement to view all shared projects, transfer ownership only to staff or admin, and delete shared projects.
```

```text
Implement admin user search, role changes, activation/deactivation, and deletion while preventing self-demotion, self-deactivation, and self-deletion.
```

```text
Here is the PythonAnywhere traceback. Explain the cause and the exact file or endpoint to fix.
```

```text
Write a detailed, project-specific README explaining local setup, PostgreSQL configuration, PythonAnywhere deployment, user workflows, security, testing, and GenAI use.
```

I also supplied:

- The assignment PDF.
- Screenshots of the application and project structure.
- Existing Python, SQL, and template snippets.
- Flask route maps.
- Git status and command output.
- PythonAnywhere error logs.
- Database test-account results.

## Responsibility and review

I remain responsible for the submitted work. I selected the final structure, integrated the code, configured the database and hosting environment, tested the application, reviewed errors, and verified the deployed behaviour. ChatGPT outputs were treated as assistance and were reviewed, adapted, and tested rather than assumed to be correct.

No other GenAI tool was intentionally used to generate the submitted application content. If another GenAI tool is used before submission, this acknowledgement will be updated.

---

# Submission checklist

- [ ] The PythonAnywhere application runs successfully.
- [ ] Student, staff, and administrator credentials in the Hand-In Sheet are correct.
- [ ] `lincolnmac` is the PythonAnywhere teacher.
- [ ] `lincolnmac` has access to the private GitHub repository.
- [ ] `create_database.sql` is committed.
- [ ] `populate_database.sql` is committed.
- [ ] `requirements.txt` is committed.
- [ ] `.gitignore` excludes the virtual environment, `connect.py`, Python caches, and compiled files.
- [ ] This complete GenAI acknowledgement is present.
- [ ] The latest tested version is deployed.
- [ ] No changes are made after submission until marks are released.

---

## Educational-use notice

LU-TODO is an educational prototype developed for COMP639. It is not an official production system of Lincoln University and should not be used to store real sensitive university information.
