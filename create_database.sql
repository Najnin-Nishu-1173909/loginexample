BEGIN;

-- Drop child tables before parent tables so this script can rebuild the schema.
DROP TABLE IF EXISTS project_members;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

-- Drop custom PostgreSQL enum types after the tables that use them.
DROP TYPE IF EXISTS task_priority;
DROP TYPE IF EXISTS user_status;
DROP TYPE IF EXISTS user_role;

-- Enum types required by the assignment.
CREATE TYPE user_role AS ENUM (
    'student',
    'staff',
    'admin'
);

CREATE TYPE user_status AS ENUM (
    'active',
    'inactive'
);

CREATE TYPE task_priority AS ENUM (
    'low',
    'medium',
    'high'
);

-- Users table.
CREATE TABLE users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    position TEXT NOT NULL,
    profile_picture TEXT,
    password_hash TEXT NOT NULL,
    user_role user_role NOT NULL,
    status user_status NOT NULL DEFAULT 'active'
);

-- Projects table.
CREATE TABLE projects (
    project_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    project_name TEXT NOT NULL,
    description TEXT,

    CONSTRAINT projects_owner_fk
        FOREIGN KEY (owner_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    -- A user cannot own two projects with the same name.
    CONSTRAINT projects_owner_project_name_unique
        UNIQUE (owner_id, project_name)
);

-- Tasks table.
CREATE TABLE tasks (
    task_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    description TEXT,
    priority task_priority NOT NULL,
    due_date DATE,
    is_complete BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT tasks_project_fk
        FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
        ON DELETE CASCADE
);

-- Junction table linking shared projects to their members.
CREATE TABLE project_members (
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,

    CONSTRAINT project_members_pk
        PRIMARY KEY (project_id, user_id),

    CONSTRAINT project_members_project_fk
        FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
        ON DELETE CASCADE,

    CONSTRAINT project_members_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

COMMIT;