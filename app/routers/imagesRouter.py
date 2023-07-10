# FastAPI
from fastapi import APIRouter, status, HTTPException, UploadFile
from fastapi import File, Query, Depends
from fastapi.responses import FileResponse
# ProfilePicMaker
from ProfilePicMaker.app.models.pictures import BigPic
from ProfilePicMaker.app.models.colors import Color, ColorExamples
# APP
from app.models.user import User
from app.models.picture import Picture
from app.dependencies.service import MakePicture
from app.security.secureuser import get_current_user
# Python
from typing import Annotated, Union
import tempfile

router = APIRouter()

LIMIT_SIZE_FREE = 3 # MB
LIMIT_SIZE_USER = 15 # MB


@router.post('/example',
    response_class=FileResponse, 
    status_code=status.HTTP_201_CREATED)
async def example(pic_file: UploadFile = File(...),
                    index: int = Query(description='Which face in the picture will be used',
                                       default=1, 
                                       ge=1, le=10), 
                    colorA: ColorExamples = Query(description='First Color to use, Default = Black',
                                                  default=ColorExamples.BLACK),
                    colorB: ColorExamples = Query(description='Last Color to use, Default = Black',
                                                  default=ColorExamples.WHITE),
                    border: Annotated[Union[ColorExamples, None], 
                                      Query(description='Border Color to use, Default = None')] = None
                     ):
    """
    Create a picture Example with specified colors and border.

    Parameters:
        pic_file (UploadFile): The picture file to process.
        index (int): Which face in the picture will be used. Default is 1. Must be between 1 and 10.
        colorA (ColorExamples): First color to use. Default is Black.
        colorB (ColorExamples): Last color to use. Default is Black.
        border (Union[ColorExamples, None]): Border color to use. Default is None.

    Returns:
        FileResponse: The processed picture file resized.
    """
    if pic_file.content_type not in ("image/jpeg",):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported content type. Supported content types are 'image/jpeg'",
            )
    if pic_file.size > 1024 * 1024 * LIMIT_SIZE_FREE:     # 3MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size is too large",
        )
    Acolor = Color.get_color_rgb(colorA.value)
    Bcolor = Color.get_color_rgb(colorB.value)
    BorderColor = None if border is None else Color.get_color_rgb(border.value)
    try:
        pic_path = await MakePicture.make_temp_picture(pic_file, 
                                                       Acolor, 
                                                       Bcolor, 
                                                       BorderColor, 
                                                       (index-1))
        return FileResponse(pic_path)
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "there was an error processing your request. Try again later",
            )

    # return {"filename": pic_file.filename,
    #         "format": pic_file.content_type,
    #         "size": pic_file.size,
    #         "sizeInBytes": round(len(pic_file.file.read())/1024,ndigits=2),
    #         "temp_file": str(temp_file.name),}


@router.post('/mypicture',
    response_class=FileResponse, 
    status_code=status.HTTP_201_CREATED)
async def get_my_picture(current_user: Annotated[User, Depends(get_current_user)], 
                         pic_file: UploadFile = File(...),
                         index: int = Query(description='Which face in the picture will be used',
                                       default=1, 
                                       ge=1, le=10), 
                         quality: int = Query(description='Quality to use, Default = Preview',
                                       default=1),
                         colorA: ColorExamples = Query(description='First Color to use, Default = Black',
                                                  default=ColorExamples.BLACK),
                         colorB: ColorExamples = Query(description='Last Color to use, Default = Black',
                                                  default=ColorExamples.WHITE),
                         border: Annotated[Union[ColorExamples, None], 
                                      Query(description='Border Color to use, Default = None')] = None
                        ):
    print(current_user)
    if current_user.is_active is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User disabled, please contact admin")
    if pic_file.content_type not in ("image/jpeg",):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported content type. Supported content types are 'image/jpeg'",
            )
    if pic_file.size > 1024 * 1024 * 15:     # 15MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size is too large",
        )
    Acolor = Color.get_color_rgb(colorA.value)
    Bcolor = Color.get_color_rgb(colorB.value)
    BorderColor = None if border is None else Color.get_color_rgb(border.value)
    try:
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
            # print(len(faces))
            index -= 1
            # faces[index].resize(300)
            faces[index].removeBG()
            faces[index].addBG(Acolor,Bcolor)
            faces[index].set_contour()
            if BorderColor is not None:
                faces[index].setBorder(BorderColor)
            faces[index].setBlur(30)
            faces[index].save(tol= 5)       # save the pic on a temp file during 5 sec
            return FileResponse(faces[index].get_path())
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "there was an error processing your request. Try again later",
            )

    return {"filename": pic_file.filename,
            "format": pic_file.content_type,
            "size": pic_file.size,
            "sizeInBytes": round(len(pic_file.file.read())/1024,ndigits=2),
            "temp_file": str(temp_file.name),}
