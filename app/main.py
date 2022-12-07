import os
from typing import Union

from fastapi import FastAPI, Depends
from pydantic import BaseModel

from config import DATABASE_URL
from auth_handler import sign_jwt, JWTBearer
from backend_db_lib.models import User, base, Layer
from backend_db_lib.manager import DatabaseManager
import json

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


@app.post("/login/")
def login_user(login_data: LoginData):
    with dbm.create_session() as session:
        # todo: add password hashing
        valid_user = session.query(User).filter(
                User.email == login_data.email
                and User.generate_hash(login_data.password) == User.password_hash
            )
    if valid_user.count() > 0:
        jwt = sign_jwt(valid_user.first().id)
        return LoginDataResponse(result=1, token=jwt)
    else:
        return LoginDataResponse(result=0, token=None)


@app.get("/layers/")
def get_layers():
    with dbm.create_session() as session:
        alllayers = session.query(Layer)
        dictlayers = []
        for row in alllayers:
            dictlayers.append(json_encoder_layer(row))
            
        return dictlayers


def json_encoder_layer(layer):
    return {"id":layer.id, "name":layer.layer_name}

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

@app.post("/layers/")
def post_layers(layer_data: AddLayerData):
    with dbm.create_session() as session:
        existing_layer = session.query(Layer).filter(
                Layer.layer_name == layer_data.layer_name
            )
        if existing_layer.count() > 0:
            return {"result": 0}
        else:
            new_layer = Layer(id = None, layer_name = layer_data.layer_name, layer_number = layer_data.layer_number, company_id = 1)
            session.add(new_layer)
            session.commit()
            return {"result": 1, "id": new_layer.id, "layer_name": new_layer.layer_name, "layer_number": new_layer.layer_number, "company_id": new_layer.company_id} 

