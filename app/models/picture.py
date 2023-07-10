# SQLModel
from . import MyModels
from sqlmodel import Field
# Python
from datetime import datetime
from uuid import UUID


class Picture(MyModels, table=True):
    id: int = Field(primary_key=True)
    type_picture: int = Field(nullable=False, default=0)    #ESto puede ser una clase Enum
    initDate : datetime = Field(default_factory=datetime.now,
                                nullable=False)
    user_id: UUID = Field(nullable=False,foreign_key="user.id")