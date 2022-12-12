import os

db_user = os.environ.get("DB_USER", "backendgang")
db_password = os.environ.get("DB_PASSWORD", "backendgang")
db_hostname = os.environ.get("DB_HOSTNAME", "db")
db_port = os.environ.get("DB_PORT", "8010")
db_name = os.environ.get("DB_NAME", "backend")

JWT_SECRET = "feaf1952d59f883ecf260a8683fed21ab0ad9a53323eca4f"
JWT_ALGORITHM = "HS256"
DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_hostname}:{db_port}/{db_name}"
LOGIN_TIME = 600
