"""Defines the PostgreSQL database connection details for this app.

These are stored in their own file so you can have separate versions for each
environment your app runs in (e.g. one for your local development environment,
and one for PythonAnywhere). If you're working in a team, each team member will
likely need their own version of connect.py.

Exclude this file from GitHub, otherwise you won't be able to have a different
version on each system.
"""
dbuser = 'postgres'  # PUT YOUR USERNAME HERE - usually "postgres"
dbpass = '512452'  # PUT YOUR PASSWORD HERE
dbhost = 'localhost'
dbport = 5432
dbname = 'loginexample'