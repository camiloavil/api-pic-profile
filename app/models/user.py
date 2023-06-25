#Python
from typing import Any, Dict, Optional, Tuple
from datetime import datetime
from uuid import UUID, uuid4
#sqlmodel
from sqlmodel import SQLModel, Field
#Pydantic
from pydantic import EmailStr, SecretStr

class UserBase(SQLModel):
    name : str = Field(min_length=3, max_length=50)
    email : EmailStr = Field(unique=True)
    # userTelegram: str = Field(unique=True, min_length=3, max_length=50)
    # city : str = Field(min_length=3, max_length=50)
    # country : str = Field(min_length=3, max_length=50)

class UserNew(UserBase):
    password: SecretStr = Field(min_length=8, max_length=50)
    class Config:
        schema_extra = {
            'example': {
                'name'      : 'Martin Criado',
                'email'     : 'user@example.com',
                'password'  : 'ThisIsMyPassword'
            }
        }

class User(UserBase, table=True):
    user_id : UUID = Field(default_factory=uuid4,
                           primary_key=True,
                           index=True,
                           nullable=False)
    initDate : datetime = Field(default_factory=datetime.now)
    pass_hash : str

class UserFB(UserBase):
    user_id : UUID
    class Config:
        schema_extra = {
            'example': {
                'name'      : 'Name of User',
                'email'     : 'email of User',
                'user_id'   : 'id of User'
            }
        }

class UserCreate(UserBase):
    class Config:
        schema_extra = {
            'example': {
                'name' : 'Nombre',
                'email' : 'user@example.com',
                'city' : 'Ciudad'
            }
        }

class UserUpdate(SQLModel):
    name  : Optional[str] = None 
    email : Optional[str] = None 
    city  : Optional[str] = None
    class Config:
        schema_extra = {
            'example': {
                'name' : 'Nombre',
                'email' : 'user@example.com',
                'city' : 'Ciudad'
            }
        }