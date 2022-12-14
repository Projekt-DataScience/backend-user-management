import os
import uvicorn
from typing import Union

from fastapi import FastAPI, Depends, Header
from pydantic import BaseModel
from fastapi.testclient import TestClient

from config import DATABASE_URL
from auth_handler import sign_jwt, JWTBearer, decode_jwt
from backend_db_lib.models import User, base, Layer, Group, Role, Company
from backend_db_lib.manager import DatabaseManager
from fastapi.middleware.cors import CORSMiddleware
import json
import pandas as pd



dbm = DatabaseManager(base, DATABASE_URL)
app = FastAPI(docs_url="/api/user_management/docs",
              redoc_url="/api/user_management/redoc",
              openapi_url="/api/user_management/openapi.json")
client = TestClient(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Login
class LoginData(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "admin@example.de",
                "password": "admin"
            }
        }


class LoginDataResponse(BaseModel):
    result: int
    token: Union[str, None]


@app.post("/api/user_management/login/")
def login_user(login_data: LoginData):
    with dbm.create_session() as session:
        # todo: add password hashing
        valid_user = session.query(User).filter(
            User.email == login_data.email
            and User.generate_hash(login_data.password) == User.password_hash
        )
        if valid_user.count() > 0:
            roleasstring = session.query(Role).get(valid_user.first().role_id)
            jwt = sign_jwt(valid_user.first().id, valid_user.first(
            ).company_id, roleasstring.role_name)
            return LoginDataResponse(result=1, token=jwt)
        else:
            return LoginDataResponse(result=0, token=None)

# Logout
@app.post("/api/user_management/logout/")
def logout_user(authorization: str | None = Header(default=None)):
    uid = decode_jwt(authorization.replace(
        "Bearer", "").strip()).get("user_id")
    with dbm.create_session() as session:
        user = session.query(User).where(User.id == uid)
    return {"result": 1, "first_name": user.first().first_name, "last_name": user.first().last_name}

# validate JWT
@app.post("/api/user_management/validateJWT/")
def validate_user(jwt: str):
    userinfo = decode_jwt(jwt.strip())
    if userinfo is not None: 
        return {"result": 1, "payload": userinfo}
    else:
        return {"result": 0, "Reason": "JWT not valid"}


# Layer abfragen
@app.get("/api/user_management/layers/")
def get_layers(authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        alllayers = session.query(Layer).where(Layer.company_id == cid).all()

        for layer in alllayers:
            layer.company = session.query(Company).get(layer.company_id)

        return {"result": 1, "data": alllayers}


# User einem Layer hinzufügen
class AddLayerToUser(BaseModel):
    layer_id: int

    class Config:
        schema_extra = {
            "example": {
                "layer_id": 2
            }
        }


@app.post("/api/user_management/user/layer/{user_id}")
def post_user_layer(user_id: int, user_layer_data: AddLayerToUser, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        urole = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("role")
        if (urole != "ceo" and urole != "admin"):
            return {"result": 0, "Reason": "No Permission"}
        else:
            user = session.query(User).filter(User.id == user_id)
            session.query(User).filter(User.id == user.first().id).update(
                {'layer_id': user_layer_data.layer_id})
            session.commit()

            if user.first().supervisor_id != None:
                supervisorid = session.query(User).get(user.first().supervisor_id).id
                supervisorlast_name = session.query(User).get(user.first().supervisor_id).last_name
                supervisorfirst_name = session.query(User).get(user.first().supervisor_id).first_name
            else:
                supervisorid = None
                supervisorlast_name = None
                supervisorfirst_name = None

            company = session.query(Company).get(user.first().company_id)
            role = session.query(Role).get(user.first().role_id)
            group = session.query(Group).get(user.first().group_id)
            layer = session.query(Layer).get(user.first().layer_id)

    return {"result": 1, "id": user.first().id, "first_name": user.first().first_name, "last_name": user.first().last_name, "email": user.first().email,  "profile_picture_url": user.first().profile_picture_url, "supervisor": {"supervisorid": supervisorid, "first_name": supervisorfirst_name, "last_name": supervisorlast_name, "last_name": supervisorlast_name}, "layer": layer,"company": company, "group": group, "role": role}


# User einer Gruppe hinzufügen
class AddLayerToGroup(BaseModel):
    group_id: int

    class Config:
        schema_extra = {
            "example": {
                "group_id": 2
            }
        }


@app.post("/api/user_management/user/group/{user_id}")
def post_user_group(user_id: int, user_group_data: AddLayerToGroup, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        urole = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("role")
        if (urole != "ceo" and urole != "admin"):
            return {"result": 0, "Reason": "No Permission"}
        else:
            user = session.query(User).filter(User.id == user_id)
            session.query(User).filter(User.id == user.first().id).update(
                {'group_id': user_group_data.group_id})
            session.commit()

            if user.first().supervisor_id != None:
                supervisorid = session.query(User).get(user.first().supervisor_id).id
                supervisorlast_name = session.query(User).get(user.first().supervisor_id).last_name
                supervisorfirst_name = session.query(User).get(user.first().supervisor_id).first_name
            else:
                supervisorid = None
                supervisorlast_name = None
                supervisorfirst_name = None

            company = session.query(Company).get(user.first().company_id)
            role = session.query(Role).get(user.first().role_id)
            group = session.query(Group).get(user.first().group_id)
            layer = session.query(Layer).get(user.first().layer_id)

    return {"result": 1, "id": user.first().id, "first_name": user.first().first_name, "last_name": user.first().last_name, "email": user.first().email,  "profile_picture_url": user.first().profile_picture_url, "supervisor": {"supervisorid": supervisorid, "first_name": supervisorfirst_name, "last_name": supervisorlast_name}, "layer": layer,"company": company, "group": group, "role": role}


# Layer hinzufügen
class AddLayerData(BaseModel):
    layer_name: str
    layer_number: int

    class Config:
        schema_extra = {
            "example": {
                "layer_name": "Sklave",
                "layer_number": 0
            }
        }


@app.post("/api/user_management/layers/")
def post_layers(layer_data: AddLayerData, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        existing_layer = session.query(Layer).filter(
            Layer.layer_name == layer_data.layer_name
            and Layer.company_id == decode_jwt(authorization.replace("Bearer", "").strip()).get("company_id")
        )
        if existing_layer.count() > 0:
            return {"result": 0, "Reason": "Layer already exists in the Company"}
        else:
            new_layer = Layer(id=None, layer_name=layer_data.layer_name, layer_number=layer_data.layer_number,
                              company_id=decode_jwt(authorization.replace("Bearer", "").strip()).get("company_id"))
            session.add(new_layer)
            session.commit()

            company = session.query(Company).get(new_layer.company_id)

            return {"result": 1, "id": new_layer.id, "layer_name": new_layer.layer_name, "layer_number": new_layer.layer_number, "company": company}


# Gruppe hinzufügen
class AddGroupData(BaseModel):
    group_name: str

    class Config:
        schema_extra = {
            "example": {
                "group_name": "Z-Promi"
            }
        }


@app.post("/api/user_management/groups/")
def post_groups(group_data: AddGroupData, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        existing_group = session.query(Group).filter(
            Group.group_name == group_data.group_name
            and Group.company_id == decode_jwt(authorization.replace("Bearer", "").strip()).get("company_id")
        )
        if existing_group.count() > 0:
            return {"result": 0, "Reason": "Group already exists in the Company"}
        else:
            new_group = Group(id=None, group_name=group_data.group_name, company_id=decode_jwt(
                authorization.replace("Bearer", "").strip()).get("company_id"))
            session.add(new_group)
            session.commit()

            company = session.query(Company).get(new_group.company_id)

            return {"result": 1, "id": new_group.id, "group_name": new_group.group_name, "company": company}


# User hinzufügen
class AddUserData(BaseModel):
    first_name: str
    last_name: str
    email: str
    password_hash: str
    supervisor_id: int
    role_id: int
    layer_id: int
    company_id: int
    group_id: int

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Franz",
                "last_name": "Hans",
                "email": "franzhand@xzy.de",
                "password_hash": "test",
                "supervisor_id": 2,
                "layer_id": 1,
                "company_id": 1,
                "group_id": 1,
                "role_id": 1

            }
        }


@app.post("/api/user_management/register/")
def register(user_data: AddUserData):
    with dbm.create_session() as session:
        existing_user = session.query(User).filter(
            User.email == user_data.email
        )
        if existing_user.count() > 0:
            return {"result": 0, "Reason": "Email already registered"}
        else:
            new_user = User(id=None, first_name=user_data.first_name, last_name=user_data.last_name, email=user_data.email, password=User.generate_hash(user_data.password_hash),
                            profile_picture_url=None, supervisor_id=user_data.supervisor_id, layer_id=user_data.layer_id, company_id=user_data.company_id, group_id=user_data.group_id, role_id=user_data.role_id)
            session.add(new_user)
            session.commit()
            return {"result": 1, "id": new_user.id, "first_name": new_user.first_name, "last_name": new_user.last_name}

# Get user info
@app.get("/api/user_management/user/{user_id}")
def get_users_group(user_id: int):
    with dbm.create_session() as session:
        userinfo = session.query(User).where(User.id == user_id).first()

        if userinfo.supervisor_id != None:
            userinfo.supervisorid = session.query(User).get(userinfo.supervisor_id).id
            userinfo.supervisorlast_name = session.query(User).get(userinfo.supervisor_id).last_name
            userinfo.supervisorfirst_name = session.query(User).get(userinfo.supervisor_id).first_name

        userinfo.company = session.query(Company).get(userinfo.company_id)
        userinfo.role = session.query(Role).get(userinfo.role_id)
        userinfo.group = session.query(Group).get(userinfo.group_id)
        userinfo.layer = session.query(Layer).get(userinfo.layer_id)
        delattr(userinfo, "password_hash")
        delattr(userinfo, "company_id")
        delattr(userinfo, "role_id")
        delattr(userinfo, "group_id")
        delattr(userinfo, "layer_id")

        return {"result": 1, "data": userinfo}


# Alle Gruppen abrufen
@app.get("/api/user_management/groups/")
def get_groups(authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        allgroups = session.query(Group).where(Group.company_id == cid).all()

        for group in allgroups:
            group.company = session.query(Company).get(group.company_id)

        return {"result": 1, "data": allgroups}


# Alle User in einem Layer abfragen
@app.get("/api/user_management/group/{group_id}")
def get_users_group_id(group_id: int, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        alluser = session.query(User).where(User.company_id == cid).where(User.group_id == group_id).all()

        for user in alluser:
            user.company = session.query(Company).get(user.company_id)
            user.role = session.query(Role).get(user.role_id)
            user.group = session.query(Group).get(user.group_id)
            user.layer = session.query(Layer).get(user.layer_id)
            delattr(user, "password_hash")
            delattr(user, "company_id")
            delattr(user, "role_id")
            delattr(user, "group_id")
            delattr(user, "layer_id")

        return {"result": 1, "data": alluser}

# (Idee: Alle Vorgesetzten einer Gruppe), hier anfänglich umgesetzt, funktioniert noch nicht ganz
# @app.get("/groups/supervisor/{group_id}/{assigned_layer_id}/{audit_layer_id}")
# def get_group_supervisor(group_id: int, assigned_layer_id: int, audit_layer_id: int ,authorization: str | None = Header(default=None)):
#     with dbm.create_session() as session:
#         cid = decode_jwt(authorization.replace("Bearer", "").strip()).get("company_id")
#         if (assigned_layer_id == audit_layer_id):
#             supervisors = session.query(User).where(User.layer_id == assigned_layer_id).all()
#             return {"result": 1, "data": supervisors}
#         else:
#             #assigned_layer_number = session.query(Layer.Layer_number).where(Layer.id == assigned_layer_id)
#             audit_layer_number = session.query(Layer.layer_number).where(Layer.id == audit_layer_id).first()

#             employee = session.query(User).where(User.group_id == group_id).where(User.layer_id == assigned_layer_id).first()
#             for i in range(audit_layer_number.layer_number-1): #Zweihöchste Layer
#                 if (i == audit_layer_number.layer_number-1): #Letzter durchlauf
#                     employee = session.query(User).where(User.id == employee.supervisor_id)
#                     return {"result": 1, "data": employee}
#                 else:
#                     employee = session.query(User).where(User.id == employee.supervisor_id).first()
        # return {"result": 1, "data": employee}

#Alle Employees vom Audit Layer zurückgeben
@app.get("/api/user_management/groups/employee/{group_id}/{audit_layer_id}") 
def get_auditlayer_employee(group_id: int, audit_layer_id: int ,authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace("Bearer", "").strip()).get("company_id")
        employeesofgroupandlayer = session.query(User).where(User.company_id == cid).where(User.layer_id == audit_layer_id).where(User.group_id == group_id).all()

        for employee in employeesofgroupandlayer:
            employee.company = session.query(Company).get(employee.company_id)
            employee.role = session.query(Role).get(employee.role_id)
            employee.group = session.query(Group).get(employee.group_id)
            employee.layer = session.query(Layer).get(employee.layer_id)
            delattr(employee, "password_hash")
            delattr(employee, "company_id")
            delattr(employee, "role_id")
            delattr(employee, "group_id")
            delattr(employee, "layer_id")

        return {"result": 1, "data": employeesofgroupandlayer}

#Alle Supervisoren im Auditlayer von den User in einer Gruppe
@app.get("/api/user_management/groups/supervisor/{audit_layer_id}")
def get_group_supervisor(audit_layer_id: int, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        useroflayer = session.query(User).where(User.company_id == cid).where(User.layer_id == audit_layer_id).all()

        for user in useroflayer:
            user.company = session.query(Company).get(user.company_id)
            user.role = session.query(Role).get(user.role_id)
            user.group = session.query(Group).get(user.group_id)
            user.layer = session.query(Layer).get(user.layer_id)
            delattr(user, "password_hash")
            delattr(user, "company_id")
            delattr(user, "role_id")
            delattr(user, "group_id")
            delattr(user, "layer_id")


        return {"result": 1, "data": useroflayer}

#Alle Employees von dem Audit_layer in einer Gruppe
@app.get("/api/user_management/groups/employee/{group_id}/{audit_layer_id}")
def get_group_employee(group_id: int, audit_layer_id: int, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        employeesofgroupandlayer = session.query(User.id, User.first_name, User.last_name, User.email, User.profile_picture_url, User.role_id, User.group_id,
                                                 User.supervisor_id, User.layer_id, User.company_id).where(User.company_id == cid).where(User.layer_id == audit_layer_id).where(User.group_id == group_id).all()

        for employeeofgroupandlayer in employeesofgroupandlayer:
            employeeofgroupandlayer.company = session.query(Company).get(employeeofgroupandlayer.company_id)
            employeeofgroupandlayer.role = session.query(Role).get(employeeofgroupandlayer.role_id)
            employeeofgroupandlayer.group = session.query(Group).get(employeeofgroupandlayer.group_id)
            employeeofgroupandlayer.layer = session.query(Layer).get(employeeofgroupandlayer.layer_id)
            delattr(employeeofgroupandlayer, "password_hash")
            delattr(employeeofgroupandlayer, "company_id")
            delattr(employeeofgroupandlayer, "role_id")
            delattr(employeeofgroupandlayer, "group_id")
            delattr(employeeofgroupandlayer, "layer_id")



        return {"result": 1, "data": employeesofgroupandlayer}




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
