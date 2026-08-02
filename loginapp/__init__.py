"""Application setup for LU-TODO."""

from flask import Flask

app = Flask(__name__)

# Used to securely sign Flask session cookies.
# Change this to your own unique value.
app.secret_key = "LU-TODO-1173909-Change-This-Secret-Key"

# Set up the PostgreSQL database connection.
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

# Import modules that contain Flask routes.
from . import user
from . import customer
from . import staff
from . import admin