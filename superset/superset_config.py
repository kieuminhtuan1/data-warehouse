# Superset specific config
ROW_LIMIT = 5000

SUPERSET_WEBSERVER_PORT = 8088

# Flask App Builder configuration
# Your App secret key
PREVIOUS_SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h'
SECRET_KEY='\2\1888D237694D70843CDBC38195215E5623EDAA74C3D47E8C4F1156\1\2\e\y\y\h'

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
# Note that the connection information to connect to the datasources
# you want to explore are managed directly in the web UI
# SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset.db'
SQLALCHEMY_DATABASE_URI = "postgresql://admin:admin@supersetdb/supersetdb"

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []
# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''
