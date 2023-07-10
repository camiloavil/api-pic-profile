# FastAPI
from fastapi import status, HTTPException
from fastapi import File
#APP
from app.models.user import User
from app.models.picture import Picture
# ProfilePicMaker
from ProfilePicMaker.app.models.pictures import BigPic
from ProfilePicMaker.app.models.colors import Color
# Python 
from typing import Optional
import tempfile

TEMPORARY_DURATION = 5

class MakePicture:
    def __init__(self,user : User) -> None:
        self.user = user
    
    @staticmethod
    async def make_temp_picture(pic_file : File, 
                                Acolor : Color, 
                                Bcolor : Color, 
                                BorderColor : Optional[Color] = None,
                                index : Optional[int] = 0):
        """
        Create a temporary picture using the provided `pic_file` and apply various image processing operations on it.

        Parameters:
            pic_file (File): The input picture file.
            Acolor (Color): The color of the foreground.
            Bcolor (Color): The color of the background.
            BorderColor (Optional[Color]): The color of the border (default: None).
            index (Optional[int]): The index of the face to process (default: 0).

        Returns:
            str: The path of the processed picture.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix=".jpg") as temp_file:
            # Save the uploaded file to the temporary file
            with open(temp_file.name, "wb") as f:
                f.write(await pic_file.read())
            # print(temp_file.name)
            faces = BigPic(temp_file.name).get_faces()
            if(len(faces) == 0):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail= "No Faces detected in the picture 'image/jpeg'",
                    )
            print(f'Number of faces detected: {len(faces)} and index: {index}')
            faces[index].resize(300)
            faces[index].removeBG()
            faces[index].addBG(Acolor,Bcolor)
            faces[index].set_contour()
            if BorderColor is not None:
                faces[index].setBorder(BorderColor)
            faces[index].setBlur(30)
            faces[index].save(tol= TEMPORARY_DURATION)       # save the pic on a temp file during 5 sec
            return faces[index].get_path()
