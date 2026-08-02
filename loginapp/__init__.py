"""Application setup for LU-TODO."""

from flask import Flask

app = Flask(__name__)

app.secret_key = "LU-TODO-1173909-Change-This-Secret-Key"

from . import connect
from . import db

db.init_db(
    app,
    connect.dbuser,
    connect.dbpass,
    connect.dbhost,
    connect.dbname,
    connect.dbport,
)

from . import user
from . import profile
from . import student
from . import student_tasks
from . import staff
from . import staff_tasks
from . import staff_sharing
from . import admin
from . import admin_tasks
from . import admin_sharing
from . import admin_projects