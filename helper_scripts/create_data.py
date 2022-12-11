# This scripts creates database schema and dummy data
# Before running this script you should have started the containers with docker-compose up
# You should have installed requirements inside requirements.txt

from backend_db_lib.manager import DatabaseManager
from backend_db_lib.models import base

DATABASE_URL = "postgresql://backendgang:backendgang@localhost:8010/backend"

db = DatabaseManager(base, DATABASE_URL)
db.drop_all()
db.create_all()
db.create_initial_data()