#Python
from typing import Optional
from datetime import datetime
from uuid import UUID
#sqlmodel
from sqlmodel import SQLModel, Field
#Pydantic
from pydantic import EmailStr

class UserBase(SQLModel):
    name : str = Field(min_length=3, max_length=50)
    email : EmailStr = Field(unique=True, min_length=3, max_length=50)
    userTelegram: str = Field(unique=True, min_length=3, max_length=50)
    city : str = Field(min_length=3, max_length=50)
    country : str = Field(min_length=3, max_length=50)

class UserLogin(UserBase):
    password: str = Field(min_length=8, max_length=50)


class User(UserBase, table=True):
    user_id : UUID = Field(primary_key=True)
    id: Optional[int] = Field(default=None)
    initDate : Optional[datetime] = None
