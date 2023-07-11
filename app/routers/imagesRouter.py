# FastAPI
from fastapi import APIRouter, status, HTTPException, UploadFile
from fastapi import File, Query, Depends
from fastapi.responses import FileResponse
# ProfilePicMaker
from ProfilePicMaker.app.models.colors import Color, ColorExamples
# APP
from app.models.user import User
from app.dependencies.service import QualityType
from app.dependencies.service import MakePicture
from app.security.secureuser import get_current_user
from app.dependencies.service import NoFaceException
# Python
from typing import Annotated, Union

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
    Create a Example picture with specified colors and border.

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
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Unsupported content type. Supported content types are 'image/jpeg'",)
    if pic_file.size > 1024 * 1024 * LIMIT_SIZE_FREE:     # 3MB
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'File size is too large, the limit is {LIMIT_SIZE_FREE}MB',)
    Acolor = Color.get_color_rgb(colorA.value)
    Bcolor = Color.get_color_rgb(colorB.value)
    BorderColor = None if border is None else Color.get_color_rgb(border.value)
    try:
        pic_path = await MakePicture.make_temp_picture(pic_file=pic_file, 
                                                       Acolor=Acolor, 
                                                       Bcolor=Bcolor, 
                                                       BorderColor=BorderColor, 
                                                       index=(index-1))
        return FileResponse(pic_path)
    except NoFaceException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail= e.message,)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail= "there was an error processing your request. Try again later",)

@router.post('/mypicture',
    response_class=FileResponse, 
    status_code=status.HTTP_201_CREATED)
async def get_my_picture(current_user: Annotated[User, Depends(get_current_user)], 
                         pic_file: UploadFile = File(...),
                         index: int = Query(description='Which face in the picture will be used',
                                       default=1, 
                                       ge=1, le=10), 
                         quality: QualityType = Query(description='Quality to use, Default = Preview',
                                       default=QualityType.PREVIEW),
                         colorA: ColorExamples = Query(description='First Color to use, Default = Black',
                                                  default=ColorExamples.BLACK),
                         colorB: ColorExamples = Query(description='Last Color to use, Default = Black',
                                                  default=ColorExamples.WHITE),
                         border: Annotated[Union[ColorExamples, None], 
                                            Query(description='Border Color to use, Default = None')] = None
                        ):
    """
    Endpoint to get a user's picture.
    
    This endpoint is used to get a user's picture. It requires authentication and supports file uploads. The user's picture can be customized with various options such as the desired face index, picture quality, color options, and border color.
    
    Parameters:
        - current_user: The current authenticated user.
        - pic_file: The uploaded picture file.
        - index: The index of the face in the picture to be used (default: 1).
        - quality: The quality to use for the picture (default: 1).
        - colorA: The first color to use for customization (default: ColorExamples.BLACK).
        - colorB: The last color to use for customization (default: ColorExamples.WHITE).
        - border: The border color to use for customization (default: None).
    
    Returns:
        - FileResponse: The response containing the user's customized picture.
    
    Raises:
        - HTTPException(status_code=status.HTTP_401_UNAUTHORIZED): If the current user is not active.
        - HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE): If the uploaded file is not in 'image/jpeg' format.
        - HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE): If the uploaded file size exceeds 15MB.
        - HTTPException(status_code=status.HTTP_409_CONFLICT): If there is no face detected in the uploaded picture.
        - HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR): If there is an error processing the request.
    """
    if current_user.is_active is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User disabled, please contact admin")
    if pic_file.content_type not in ("image/jpeg",):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Unsupported content type. Supported content types are 'image/jpeg'",)
    if pic_file.size > 1024 * 1024 * LIMIT_SIZE_USER:     # 15MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'File size is too large, the limit is {LIMIT_SIZE_USER} MB',
        )
    
    newPicture = MakePicture(current_user)
    Acolor = Color.get_color_rgb(colorA.value)
    Bcolor = Color.get_color_rgb(colorB.value)
    BorderColor = None if border is None else Color.get_color_rgb(border.value)

    try:
        pic_path = await newPicture.make_user_picture(pic_file=pic_file, 
                                                      Acolor=Acolor, 
                                                      Bcolor=Bcolor, 
                                                      BorderColor=BorderColor, 
                                                      quality=quality, 
                                                      index=(index-1))
        return FileResponse(pic_path)
    except NoFaceException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail= e.message,)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail= "there was an error processing your request. Try again later",)
