import os
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
app = FastAPI()


@app.get("/test/")
def read_root():
    return {"Hello": "World"}


@app.post("/admin/", dependencies=[Depends(JWTBearer())])
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

#Login
@app.post("/login/") 
def login_user(login_data: LoginData):
    with dbm.create_session() as session:
        # todo: add password hashing
        valid_user = session.query(User).filter(
                User.email == login_data.email
                and User.generate_hash(login_data.password) == User.password_hash
            )
        if valid_user.count() > 0:
            roleasstring = session.query(Role).get(valid_user.first().role_id)
            jwt = sign_jwt(valid_user.first().id, valid_user.first().company_id, roleasstring.role_name)
            return LoginDataResponse(result=1, token=jwt)
        else:
            return LoginDataResponse(result=0, token=None)

#Logout

#Layer abfragen
@app.get("/layers/") 
def get_layers(authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace("Bearer", "").strip()).get("company")
        alllayers = session.query(Layer).where(Layer.company_id == cid).all()
        return alllayers



def json_encoder_layer(layer):
    return {"id":layer.id, "name":layer.layer_name}


#User einem Layer hinzufügen

#User einer Gruppe hinzufügen

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

#Layer hinzufügen
@app.post("/layers/") 
def post_layers(layer_data: AddLayerData, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        existing_layer = session.query(Layer).filter(
                Layer.layer_name == layer_data.layer_name
                and Layer.company_id == decode_jwt(authorization.replace("Bearer", "").strip()).get("company")
            )
        if existing_layer.count() > 0:
            return {"result": 0}
        else:
            new_layer = Layer(id = None, layer_name = layer_data.layer_name, layer_number = layer_data.layer_number, company_id = decode_jwt(authorization.replace("Bearer", "").strip()).get("company"))
            session.add(new_layer)
            session.commit()
            return {"result": 1, "id": new_layer.id, "layer_name": new_layer.layer_name, "layer_number": new_layer.layer_number, "company_id": new_layer.company_id} 


class AddGroupData(BaseModel):
    group_name: str

    class Config:
        schema_extra = {
            "example": {
                "group_name": "Z-Promi"
            }
        }

#Gruppe hinzufügen
@app.post("/groups/") 
def post_groups(group_data: AddGroupData, authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        existing_group = session.query(Group).filter(
                Group.group_name == group_data.group_name
                and Group.company_id == decode_jwt(authorization.replace("Bearer", "").strip()).get("company")
            )
        if existing_group.count() > 0:
            return {"result": 0}
        else:
            new_group = Group(id = None, group_name = group_data.group_name, company_id = decode_jwt(authorization.replace("Bearer", "").strip()).get("company"))
            session.add(new_group)
            session.commit()
            return {"result": 1, "id": new_group.id, "group_name": new_group.group_name, "company_id": new_group.company_id} 


#Alle Gruppen abrufen
@app.get("/groups/") 
def get_groups(authorization: str | None = Header(default=None)):
    with dbm.create_session() as session:
        cid = decode_jwt(authorization.replace("Bearer", "").strip()).get("company")
        allgroups = session.query(Group).where(Group.company_id == cid).all()
            
        return allgroups


#Alle User in einem Layer abfragen

#Alle Gruppen unter einem gegebenen Layer abrufen

#Audit: Muss noch genauer spezifiziert werden

#Offene Audits für eine User

#Get all Questions

#Frage erstellen

#Fragenantworten

#Neues (spontanes) Audit erstellen

#Alle Audits abfragen

#Audit durchführen

#Geplantes Audit / Rhytmus / Reccurence erstellen

#Geplante Audits / Rhytmus abfragen

#Aktuelle Aufgaben






