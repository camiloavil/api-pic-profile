# FastAPI
from fastapi import File
#APP
from app.models.user import User
from app.models.picture import Picture
# ProfilePicMaker
from ProfilePicMaker.app.models.pictures import BigPic
from ProfilePicMaker.app.models.colors import Color
# Python 
from typing import Optional
from enum import Enum
import tempfile

TEMPORARY_DURATION = 5

class NoFaceException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

class QualityType(str, Enum):
    THUMBNAIL = 'thumbnail'
    PREVIEW = 'preview'
    MEDIUM = 'medium'
    HIGH = 'high'
    FULLSIZE = 'fullsize'

class MakePicture:
    def __init__(self,user : User) -> None:
        self.user = user

    async def make_user_picture(self, 
                                pic_file : File, 
                                Acolor : Color, 
                                Bcolor : Color, 
                                BorderColor : Optional[Color] = None,
                                quality : QualityType = QualityType.PREVIEW,
                                index : Optional[int] = 0) -> str:
        print('lets create a picture for a user') 
        print(self.user)
    
    @staticmethod
    async def make_temp_picture(pic_file : File, 
                                Acolor : Color, 
                                Bcolor : Color, 
                                BorderColor : Optional[Color] = None,
                                quality : Optional[QualityType] = QualityType.PREVIEW,
                                index : Optional[int] = 0) -> str:
        """
        Creates a temporary picture with the specified parameters.

        Parameters:
            pic_file (File): The picture file to be used.
            Acolor (Color): The color for the A component.
            Bcolor (Color): The color for the B component.
            BorderColor (Optional[Color], optional): The color for the border. Defaults to None.
            quality (Optional[QualityType], optional): The quality type of the picture. Defaults to QualityType.PREVIEW.
            index (Optional[int], optional): The index of the face. Defaults to 0.

        Returns:
            str: The path of the temporary picture.
        """

        with tempfile.NamedTemporaryFile(delete=True, suffix=".jpg") as temp_file:
            with open(temp_file.name, "wb") as f:
                f.write(await pic_file.read())
            faces = BigPic(temp_file.name).get_faces()
            if(len(faces) == 0):
                raise NoFaceException("No Faces detected in the picture 'image/jpeg'")

            if quality == QualityType.THUMBNAIL:
                faces[index].resize(150)
            elif quality == QualityType.PREVIEW:
                faces[index].resize(300)
            elif quality == QualityType.MEDIUM:
                faces[index].resize(600)
            elif quality == QualityType.HIGH:
                faces[index].resize(100)

            faces[index].removeBG()
            faces[index].addBG(Acolor,Bcolor)
            faces[index].set_contour()
            if BorderColor is not None:
                faces[index].setBorder(BorderColor)
            faces[index].setBlur(30)
            faces[index].save(tol= TEMPORARY_DURATION)       # save the pic on a temp file during 5 sec
            return faces[index].get_path()
