# FastAPI
from fastapi import File
#APP
from app.DB.db import BASE_DIR
from app.DB.querys_pictures import PictureDB
from app.models.picture import Picture, Free_picture, QualityType, FreeQualityType
from app.models.user import User
# SQLModel
from sqlmodel import Session
# ProfilePicMaker
from ProfilePicMaker.app.models.pictures import BigPic
from ProfilePicMaker.app.models.colors import Color
# Python 
from typing import Optional
import tempfile
import shutil
import os

TEMPORARY_DURATION = 5 #Seconds

class NoFaceException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

class MakePicture:
    def __init__(self,user : User) -> None:
        self.user = user

    async def make_user_picture(self, 
                                db : Session,
                                pic_file : File,
                                colorsModel : tuple(Color),
                                BorderColor : Optional[Color] = None,
                                quality : QualityType = QualityType.PREVIEW,
                                index : Optional[int] = 0) -> str:
        print('lets create a picture for a user') 
        print(self.user)
        print(self.user.id)
        user_path_directory = os.path.join(os.path.dirname(BASE_DIR),
                                           'resources',
                                           str(self.user.id))
        print(f'user_path_directory: {user_path_directory}')
        # check if the user has a folder_user if not create it whit id of user
        # if not os.path.exists(user_path_directory):
        os.makedirs(user_path_directory, exist_ok=True)

        # make the pic and save it into the folder whit the user idname
        pic_file = await MakePicture.make_temp_picture(pic_file = pic_file,
                                                    colorsModel = colorsModel,
                                                    BorderColor = BorderColor, 
                                                    quality = quality, 
                                                    index = index,
                                                    temp = False)
        sequence = 0
        pic_file_parts = os.path.splitext(os.path.basename(pic_file))
        pic_filename = f"{pic_file_parts[0]}_{quality}_{sequence}{pic_file_parts[1]}"
        new_pic_path = os.path.join(user_path_directory, pic_filename)
        shutil.move(pic_file, new_pic_path)
        # create db log of the picture
        pictureDB = Picture(filename=pic_filename, 
                            user_id=self.user.id, 
                            type_picture=quality)
        
        PictureDB.add_picture_toDB(pictureDB, db)
        return new_pic_path
    
    @staticmethod
    async def make_temp_picture(pic_file : File, 
                                colorsModel : tuple(Color),
                                BorderColor : Optional[Color] = None,
                                quality : Optional[QualityType] = QualityType.PREVIEW,
                                index : Optional[int] = 0,
                                temp : bool = True) -> str:
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
        print(f'test Colors {colorsModel} {str(colorsModel[0])} {str(colorsModel[1])}')
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
                faces[index].resize(1000)

            faces[index].removeBG()
            # faces[index].addBG(Acolor,Bcolor)
            faces[index].addBG(colorsModel)
            faces[index].set_contour()
            if BorderColor is not None:
                faces[index].setBorder(BorderColor)
            faces[index].setBlur(30)
            if temp:
                faces[index].save(tol= TEMPORARY_DURATION)       # save the pic on a temp file during 5 sec
            else:
                faces[index].save()
            return faces[index].get_path()
