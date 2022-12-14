from main import client
import random
import string

token = ""
jwt_token =""

def generate_random_email():
  return "".join(random.choices(string.ascii_uppercase + string.digits, k=10)) + "@email.com"

def generate_random_name():
  return "".join(random.choices(string.ascii_uppercase + string.digits, k=15))

def test_login():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("result") == 1
    assert response.json().get("token") is not None
    jwt_token = response.json().get("token") 

def test_get_groups():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.get("/api/user_management/groups", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("result") == 1

def test_logout():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.post("/api/user_management/logout", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("result") == 1

def test_register():
    data = {
        "first_name": "Franz",
        "last_name": "Hans",
        "email": generate_random_email(),
        "password_hash": "test",
        "supervisor_id": 2,
        "layer_id": 1,
        "company_id": 1,
        "group_id": 1,
        "role_id": 1
    }

    response = client.post("/api/user_management/register", json=data)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("result") == 1

def test_userInfo_abfragen():
    response = client.get("/api/user_management/user/1")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("result") == 1

def test_validateJWT():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.post("/api/user_management/validateJWT?jwt=" + token)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("result") == 1


def test_get_layers():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.get("/api/user_management/layers", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_add_user_to_layer():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }
    data2= {
        "layer_id": 2
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.post("/api/user_management/user/layer/3", headers={"Authorization":f"Bearer {token}"}, json=data2)
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_add_User_to_group():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }
    data2= {
        "group_id": 2
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.post("/api/user_management/user/group/3", headers={"Authorization":f"Bearer {token}"}, json=data2)
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_add_layer():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }
    data2= {
        "layer_name": generate_random_name(),
        "layer_number": 0
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.post("/api/user_management/layers", headers={"Authorization":f"Bearer {token}"}, json=data2)
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_add_group():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }
    data2= {
        "group_name": generate_random_name()
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.post("/api/user_management/groups", headers={"Authorization":f"Bearer {token}"}, json=data2)
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_get_all_groups():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.get("/api/user_management/groups", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_get_all_user_in_group():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.get("/api/user_management/group/2", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_get_all_employee_in_groups():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.get("/api/user_management/groups/employee/1/1", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1

def test_get_all_supervisor_in_groups():
    data = {
        "email": "josef@test.de",
        "password": "test"
    }

    response = client.post("/api/user_management/login", json=data)
    token = response.json().get("token")

    response = client.get("/api/user_management/groups/supervisor/1", headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 
    assert response.json().get("result") == 1