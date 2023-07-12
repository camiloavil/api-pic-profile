# SQLModel
from . import MyModels
from sqlmodel import Field
# Python
from datetime import datetime
from enum import Enum
from uuid import UUID

class QualityType(str, Enum):
    THUMBNAIL = 'thumbnail'
    PREVIEW = 'preview'
    MEDIUM = 'medium'
    HIGH = 'high'
    FULLSIZE = 'fullsize'

class Picture(MyModels, table=True):
    id: int = Field(primary_key=True)
    type_picture: QualityType = Field(nullable=False, default=QualityType.PREVIEW)    #ESto puede ser una clase Enum
    initDate : datetime = Field(default_factory=datetime.now,
                                nullable=False)
    user_id: UUID = Field(nullable=False,foreign_key="user.id")