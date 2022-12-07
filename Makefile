export ALGORITHM="HS256"
export SECRET="feaf1952d59f883ecf260a8683fed21ab0ad9a53323eca4f"
export DATABASE_URL="postgresql://backendgang:backendgang@db:8010"
install:
	pip install -r requirements.txt

run: install
	uvicorn app.main:app --host 0.0.0.0 --reload --log-level 'debug'