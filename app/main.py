import os
import uvicorn
from typing import Union

from fastapi import FastAPI, Depends, Header
from pydantic import BaseModel

from config import DATABASE_URL
from auth_handler import sign_jwt, JWTBearer, decode_jwt
from backend_db_lib.models import User, base, Layer, Group, Role
from backend_db_lib.manager import DatabaseManager
import json
import pandas as pd

dbm = DatabaseManager(base, DATABASE_URL)
app = FastAPI(docs_url="/api/user_management/docs",
              redoc_url="/api/user_management/redoc")


@app.get("/api/user_management/test/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/user_management/admin/", dependencies=[Depends(JWTBearer())])
def logged_content():
    return {"Hello": "Admin"}


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

# Login


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


# Layer abfragen
@app.get("/api/user_management/layers/")
def get_layers(authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        alllayers = session.query(Layer).where(Layer.company_id == cid).all()
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

    return {"result": 1, "id": user.first().id, "first_name": user.first().first_name, "last_name": user.first().last_name, "email": user.first().email,  "profile_picture_url": user.first().profile_picture_url, "supervisor_id": user.first().supervisor_id, "layer_id": user.first().layer_id, "company_id": user.first().company_id, "group_id": user.first().group_id, "role_id": user.first().role_id}


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

    return {"result": 1, "id": user.first().id, "first_name": user.first().first_name, "last_name": user.first().last_name, "email": user.first().email, "profile_picture_url": user.first().profile_picture_url, "supervisor_id": user.first().supervisor_id, "layer_id": user.first().layer_id, "company_id": user.first().company_id, "group_id": user.first().group_id, "role_id": user.first().role_id}


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
            return {"result": 0}
        else:
            new_layer = Layer(id=None, layer_name=layer_data.layer_name, layer_number=layer_data.layer_number,
                              company_id=decode_jwt(authorization.replace("Bearer", "").strip()).get("company_id"))
            session.add(new_layer)
            session.commit()
            return {"result": 1, "id": new_layer.id, "layer_name": new_layer.layer_name, "layer_number": new_layer.layer_number, "company_id": new_layer.company_id}


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
            return {"result": 0}
        else:
            new_group = Group(id=None, group_name=group_data.group_name, company_id=decode_jwt(
                authorization.replace("Bearer", "").strip()).get("company_id"))
            session.add(new_group)
            session.commit()
            return {"result": 1, "id": new_group.id, "group_name": new_group.group_name, "company_id": new_group.company_id}

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
def post_groups(user_data: AddUserData):
    with dbm.create_session() as session:
        existing_user = session.query(User).filter(
            User.email == user_data.email
        )
        if existing_user.count() > 0:
            return {"result": 0, "Reason": "Email registered"}
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
        userinfo = session.query(User.id, User.first_name, User.last_name, User.email, User.profile_picture_url, User.role_id,
                                 User.group_id, User.supervisor_id, User.layer_id, User.company_id).where(User.id == user_id).all()

        return {"result": 1, "data": userinfo}


# Alle Gruppen abrufen
@app.get("/api/user_management/groups/")
def get_groups(authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        allgroups = session.query(Group).where(Group.company_id == cid).all()

        return {"result": 1, "data": allgroups}


# Alle User in einem Layer abfragen
@app.get("/api/user_management/groups/{group_id}")
def get_users_group(group_id: int, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        alluser = session.query(User.id, User.first_name, User.last_name, User.email, User.profile_picture_url, User.role_id, User.group_id,
                                User.supervisor_id, User.layer_id, User.company_id).where(User.company_id == cid).where(User.group_id == group_id).all()

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

# Alle nutzer vom Audit Layer zurückgeben


@app.get("/api/user_management/groups/supervisor/{audit_layer_id}")
def get_group_supervisor(audit_layer_id: int, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        useroflayer = session.query(User.id, User.first_name, User.last_name, User.email, User.profile_picture_url, User.role_id, User.group_id,
                                    User.supervisor_id, User.layer_id, User.company_id).where(User.company_id == cid).where(User.layer_id == audit_layer_id).all()
        return {"result": 1, "data": useroflayer}


@app.get("/api/user_management/groups/employee/{group_id}/{audit_layer_id}")
def get_group_employee(group_id: int, audit_layer_id: int, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace(
            "Bearer", "").strip()).get("company_id")
        employeesofgroupandlayer = session.query(User.id, User.first_name, User.last_name, User.email, User.profile_picture_url, User.role_id, User.group_id,
                                                 User.supervisor_id, User.layer_id, User.company_id).where(User.company_id == cid).where(User.layer_id == audit_layer_id).where(User.group_id == group_id).all()
        return {"result": 1, "data": employeesofgroupandlayer}


# Audit: Muss noch genauer spezifiziert werden

# Offene Audits für eine User

# Get all Questions

# Frage erstellen

# Fragenantworten

# Neues (spontanes) Audit erstellen

# Alle Audits abfragen

# Audit durchführen

# Geplantes Audit / Rhytmus / Reccurence erstellen

# Geplante Audits / Rhytmus abfragen

# Aktuelle Aufgaben


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
