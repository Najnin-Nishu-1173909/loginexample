from pathlib import Path
import subprocess

first_names = [
    "Aarav","Aisha","Akira","Amelia","Aria","Benjamin","Charlotte","Daniel","Ethan","Eva",
    "Fatima","Finn","Grace","Hana","Harper","Henry","Isla","Jack","James","Jasmine",
    "Kai","Layla","Leo","Liam","Lily","Lucas","Maya","Mia","Noah","Nora",
    "Oliver","Olivia","Oscar","Priya","Riley","Ruby","Samuel","Sofia","Sophie","Tane",
    "Theo","Thomas","Victoria","William","Yuki","Zara","Zoe","Anika","Caleb","Mei",
    "Alice","Brian","Catherine","David","Emma","George","Helen","Ian","Julia","Kevin",
    "Laura","Michael"
]
last_names = [
    "Anderson","Baker","Chen","Davis","Evans","Fisher","Garcia","Harris","Ito","Jones",
    "Kaur","Lee","Martin","Ngata","O'Connor","Patel","Quinn","Roberts","Singh","Taylor",
    "Upton","Walker","Xu","Young","Zhang","Brown","Clark","Edwards","Fraser","Green",
    "Hall","King","Lewis","Mitchell","Nelson","Owens","Parker","Reid","Scott","Turner",
    "Wilson","Adams","Bell","Cooper","Dunn","Ellis","Ford","Gray","Hughes","Irwin",
    "Kelly","Morgan","Nash","Price","Russell","Stewart","Thompson","Ward","White","Wood",
    "Wright","Murray"
]

def bcrypt_hash(password: str) -> str:
    result = subprocess.run(
        ["htpasswd", "-bnBC", "12", "", password],
        check=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split(":", 1)[1]

def esc(value: str) -> str:
    return value.replace("'", "''")

user_rows = []
credentials = []

for i, (first, last) in enumerate(zip(first_names, last_names), start=1):
    role = "student" if i <= 50 else ("staff" if i <= 60 else "admin")
    domain = "lincolnuni.ac.nz" if role == "student" else "lincoln.ac.nz"
    email = f"{first.lower().replace(' ', '').replace(chr(39), '')}.{last.lower().replace(' ', '').replace(chr(39), '')}@{domain}"
    password = f"LuTodo{i:02d}!"
    password_hash = bcrypt_hash(password)

    if role == "student":
        student_positions = [
            "Bachelor of Commerce Student",
            "Master of Applied Computing Student",
            "Bachelor of Agricultural Science Student",
            "Postgraduate Research Student"
        ]
        position = student_positions[(i - 1) % len(student_positions)]
    elif role == "staff":
        staff_positions = [
            "Lecturer in Applied Computing",
            "Research Coordinator",
            "Programme Administrator",
            "Senior Tutor",
            "Academic Services Adviser"
        ]
        position = staff_positions[(i - 51) % len(staff_positions)]
    else:
        position = "System Administrator"

    profile_picture = "NULL"
    status = "inactive" if i in (15, 57) else "active"

    user_rows.append(
        f"('{esc(email)}', '{esc(first)}', '{esc(last)}', '{esc(position)}', "
        f"{profile_picture}, '{password_hash}', '{role}', '{status}')"
    )
    credentials.append((email, password, role, status))

sql = """-- LU-TODO database population script
-- COMP639 Individual Assignment, Semester 2, 2026
-- Run this after create_database.sql.

BEGIN;

TRUNCATE TABLE project_members, tasks, projects, users
RESTART IDENTITY CASCADE;

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
VALUES
""" + ",\n".join("    " + row for row in user_rows) + """;

-- Create 100 realistic projects.
-- The first 40 are owned by staff/admin users so they can be shared.
INSERT INTO projects (owner_id, project_name, description)
SELECT
    CASE
        WHEN project_number <= 40
            THEN 51 + ((project_number - 1) % 12)
        ELSE 1 + ((project_number - 41) % 62)
    END,
    CASE ((project_number - 1) % 10)
        WHEN 0 THEN 'Teaching Preparation ' || project_number
        WHEN 1 THEN 'Research Milestones ' || project_number
        WHEN 2 THEN 'Coursework Planner ' || project_number
        WHEN 3 THEN 'Student Support Actions ' || project_number
        WHEN 4 THEN 'Laboratory Activities ' || project_number
        WHEN 5 THEN 'Professional Development ' || project_number
        WHEN 6 THEN 'Community Engagement ' || project_number
        WHEN 7 THEN 'Assessment Schedule ' || project_number
        WHEN 8 THEN 'Sustainability Initiative ' || project_number
        ELSE 'Semester Priorities ' || project_number
    END,
    CASE ((project_number - 1) % 6)
        WHEN 0 THEN 'Plan and track teaching-related activities for the semester.'
        WHEN 1 THEN 'Coordinate research tasks, reviews, and key deliverables.'
        WHEN 2 THEN 'Organise coursework, deadlines, and study priorities.'
        WHEN 3 THEN 'Record follow-up actions for student and staff support.'
        WHEN 4 THEN 'Prepare resources, bookings, and safety checks.'
        ELSE 'Track important university work and completion progress.'
    END
FROM generate_series(1, 100) AS project_number;

-- Create exactly 500 tasks: five for each project.
INSERT INTO tasks (
    project_id,
    task_name,
    description,
    priority,
    due_date,
    is_complete
)
SELECT
    project_id,
    CASE task_number
        WHEN 1 THEN 'Review project requirements'
        WHEN 2 THEN 'Prepare supporting resources'
        WHEN 3 THEN 'Complete the main activity'
        WHEN 4 THEN 'Check progress with stakeholders'
        ELSE 'Final review and close-out'
    END,
    CASE task_number
        WHEN 1 THEN 'Read the project information and confirm the expected outcomes.'
        WHEN 2 THEN 'Gather the files, references, and resources needed for the work.'
        WHEN 3 THEN 'Carry out the central piece of work for this project.'
        WHEN 4 THEN 'Confirm progress, resolve issues, and record follow-up actions.'
        ELSE 'Check quality, update completion status, and document the result.'
    END,
    CASE ((project_id + task_number) % 3)
        WHEN 0 THEN 'low'::task_priority
        WHEN 1 THEN 'medium'::task_priority
        ELSE 'high'::task_priority
    END,
    CASE ((project_id + task_number) % 5)
        WHEN 0 THEN NULL
        WHEN 1 THEN CURRENT_DATE - ((project_id % 20) + 1)
        WHEN 2 THEN CURRENT_DATE + ((project_id % 30) + 1)
        WHEN 3 THEN CURRENT_DATE - ((project_id % 10) + 1)
        ELSE CURRENT_DATE + ((project_id % 45) + 1)
    END,
    ((project_id + task_number) % 4 = 0)
FROM projects
CROSS JOIN generate_series(1, 5) AS task_number;

-- Give every user membership in at least one shared staff/admin project.
INSERT INTO project_members (project_id, user_id)
SELECT
    1 + ((user_id + 1) % 12),
    user_id
FROM users;

-- Add 38 additional unique memberships, producing exactly 100 total.
INSERT INTO project_members (project_id, user_id)
SELECT
    13 + ((user_id + 4) % 12),
    user_id
FROM users
WHERE user_id <= 38;

COMMIT;

-- Verification output.
SELECT user_role, COUNT(*) AS user_count
FROM users
GROUP BY user_role
ORDER BY user_role;

SELECT COUNT(*) AS project_count FROM projects;
SELECT COUNT(*) AS task_count FROM tasks;
SELECT COUNT(*) AS project_member_count FROM project_members;

SELECT COUNT(*) AS users_without_shared_project
FROM users u
WHERE NOT EXISTS (
    SELECT 1
    FROM project_members pm
    WHERE pm.user_id = u.user_id
);
"""

sql_path = Path("/mnt/data/populate_database.sql")
sql_path.write_text(sql, encoding="utf-8")

credentials_text = [
    "# LU-TODO test credentials",
    "",
    "Keep this file private. Do not commit it to a public repository.",
    "",
    "| Email | Password | Role | Status |",
    "|---|---|---|---|"
]
credentials_text.extend(
    f"| {email} | {password} | {role} | {status} |"
    for email, password, role, status in credentials
)

credentials_path = Path("/mnt/data/LU_TODO_test_credentials.md")
credentials_path.write_text("\n".join(credentials_text), encoding="utf-8")

print(f"Created {sql_path} ({sql_path.stat().st_size:,} bytes)")
print(f"Created {credentials_path}")
