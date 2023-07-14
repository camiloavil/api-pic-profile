# SQLModel
from . import MyModels
from sqlmodel import Field
# Python
from enum import Enum
from uuid import UUID
from datetime import datetime

class QualityType(str, Enum):
    THUMBNAIL = 'thumbnail'
    PREVIEW = 'preview'
    MEDIUM = 'medium'
    HIGH = 'high'
    FULLSIZE = 'fullsize'

class FreeQualityType(str, Enum):
    THUMBNAIL = 'thumbnail'
    PREVIEW = 'preview'

class Picture(MyModels, table=True):
    id: int = Field(primary_key=True)
    filename : str = Field(nullable=False)
    type_picture: QualityType = Field(nullable=False, 
                                      default=QualityType.PREVIEW)    
    initDate : datetime = Field(default_factory=datetime.now,
                                nullable=False)
    user_id: UUID = Field(nullable=False,foreign_key="user.id")

class Free_picture(MyModels, table=True):
    id: int = Field(primary_key=True)
    ip: str = Field(nullable=False)
    quality: FreeQualityType = Field(nullable=False, 
                                          default=QualityType.PREVIEW) 
    date : datetime = Field(default_factory = datetime.now,
                            nullable=False)
    # user_id: UUID = Field(nullable=True,
    #                       default=None,
    #                       foreign_key="user.id")