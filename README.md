# backend-user_management

# Starting dev environment

1. Start the docker images:

```
docker-compose up
```

2. Create virtualenv:

```
virtualenv venv
```

3. Activate the virtualenv

Windows:

```
./venv/Scripts/activate
```

Linux:

```
source ./venv/bin/activate
```

4. Install requirements

```
pip install -r requirements.txt
```

5. Create database schema and dummy data

```
python ./helper_scripts/create_data.py
```

The user-management service is running on port 8001, you can access the docs on http://localhost:8001/docs
