# SQLModel
from sqlmodel import SQLModel, Field
# Python
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime
from pydantic import SecretStr, EmailStr

class UserBase(SQLModel):
    name  : str = Field(min_length=3, max_length=50)
    email : EmailStr = Field(unique=True)
    city : Optional[str] = Field(default= None, min_length=3, max_length=50)
    country : Optional[str] = Field(default= None, min_length=3, max_length=50)

class User(UserBase, table=True):
    user_id : UUID = Field(default_factory=uuid4,
                           primary_key=True,
                           index=True,
                           nullable=False)
    is_active : bool = Field(default=True,
                             nullable=False)
    initDate : datetime = Field(default_factory=datetime.now,
                                nullable=False)
    userType : str = Field(default='free',
                           nullable=False)
    idTelegram : Optional[int] = None
    pass_hash : str 

class UserCreate(UserBase):
    password : SecretStr = Field(min_length=8, max_length=50)
    class Config:
        schema_extra = {
            'example': {
                'name'      : 'Example Herrera',
                'email'     : 'user@example.com',
                'password'  : 'MyPassword',
                'city'      : 'City of User [Optional]',
                'country'   : 'Country of User [Optional]',
            }
        }

class UserFB(UserBase):
    user_id : UUID
    initDate : datetime
    userType : str 
    class Config:
        schema_extra = {
            'example': {
                'user_id'   : 'id of User',
                'name'      : 'Name of User',
                'email'     : 'email of User',
                'initDate'  : 'Date of Creation of User',
                'userType'  : 'Category of User',
            }
        }

class UserUpdate(SQLModel):
    name  : Optional[str] = Field(min_length=3, max_length=50) 
    country : Optional[str] = Field(default= None, min_length=3, max_length=50)
    city  : Optional[str] = Field(default= None, min_length=3, max_length=50)
    class Config:
        schema_extra = {
            'example': {
                'name'    : 'Name to change',
                'country' : 'Country to change',
                'city'    : 'City to change',
            }
        }
