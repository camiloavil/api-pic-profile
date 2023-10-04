# FastAPI
from fastapi import APIRouter, status, HTTPException, UploadFile, Request
from fastapi import Path, Query, Depends
from fastapi.responses import FileResponse
# APP
from app.models.user import User
from app.models.picture import QualityType, FreeQualityType, Free_picture
from app.DB.db import get_session
from app.DB.querys_pictures import FreePictureDB
from app.dependencies.service import MakePicture
from app.security.secureuser import get_current_user
from app.dependencies.service import NoFaceException
# SQLModel
from sqlmodel import Session
# Python
from pydantic.color import Color
from typing import Annotated, Union
from datetime import datetime

router = APIRouter()

LIMIT_SIZE_FREE = 15  # MB
LIMIT_SIZE_USER = 30  # MB

LIMIT_FREE_PICTURES = 60


@router.post('/example/{quality}',
             response_class=FileResponse,
             status_code=status.HTTP_201_CREATED)
async def example(
    request: Request,
    picture_file: UploadFile,
    db: Session = Depends(get_session),
    index: int = Query(description='Which face in the picture will be used',
                       default=1, ge=1, le=10),
    quality: FreeQualityType = Path(description='Quality to use'),
    colorCenter: Color = Query(description='Center Color, the value could be RGB or HEX as CSS3 standard https://www.w3.org/TR/css-color-3/#svg-color',
                               default='black'),
    colorOuter: Color = Query(description='Outer Color, the value could be RGB or HEX as CSS3 standard https://www.w3.org/TR/css-color-3/#svg-color',
                              default='white'),
    colorBorder: Annotated[Union[Color, None],
                           Query(description='Border Color to use, Default = None')] = None
):
    """
    Endpoint for uploading an example picture.  

    Parameters:  
        - `quality` (FreeQualityType, Path): The quality to use.  
        - `index` (int, Query, optional): The index of the face in the picture to be used. Must be between 1 and 10. Defaults to 1.  
        - `colorCenter` (Color, Query, optional): The center color. The value could be RGB or HEX as per the CSS3 standard. Defaults to 'black'.  
        - `colorOuter` (Color, Query, optional): The outer color. The value could be RGB or HEX as per the CSS3 standard. Defaults to 'white'.  
        - `colorBorder` (Union[Color, None], Query, optional): The border color to use. Defaults to None.  
        - `picture_file` (UploadFile): The uploaded picture file.  

    Returns:
        - `FileResponse`: The response object containing the uploaded picture.
    """

    nPics_ip = FreePictureDB.get_count_ip_date(ip=request.client.host,
                                               date=datetime.now(),
                                               db=db)
    print(f'{request.client.host}: Number of pictures: {nPics_ip}')
    if nPics_ip > LIMIT_FREE_PICTURES:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f'You have reached the limit of {LIMIT_FREE_PICTURES} pictures by day. Please register your user to get unlimited pictures',)

    if picture_file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Unsupported content type. Supported content types are 'image/jpeg' or 'image/png'",)
    if picture_file.size > 1024 * 1024 * LIMIT_SIZE_FREE:     # 3MB
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'File size is too large, the limit is {LIMIT_SIZE_FREE}MB',)

    try:
        pic_path = await MakePicture.make_temp_picture(pic_file=picture_file,
                                                       colorsModel=(colorCenter,
                                                                    colorOuter),
                                                       BorderColor=colorBorder,
                                                       quality=quality,
                                                       index=(index-1))
    except NoFaceException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=e.message,)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="there was an error processing your request. Try again later",)
    FreePictureDB.add_freePicture_toDB(Free_picture(ip=request.client.host,
                                                    quality=quality),
                                       db=db)

    headers = {
        'Access-Control-Expose-Headers': 'Content-Disposition',
        'picMaker-pics-left-day': f'{LIMIT_FREE_PICTURES - nPics_ip}'
    }
    return FileResponse(pic_path, headers=headers, media_type="image/png", filename='example.png')


@router.post('/mypicture/{quality}',
             response_class=FileResponse,
             status_code=status.HTTP_201_CREATED)
async def get_my_picture(
    current_user: Annotated[User, Depends(get_current_user)],
    pic_file: UploadFile,
    db: Session = Depends(get_session),
    index: int = Query(description='Which face in the picture will be used',
                       default=1,
                       ge=1, le=10),
    quality: QualityType = Path(description='Quality to use'),
    colorCenter: Color = Query(description='Center Color, the value could be RGB or HEX as CSS3 standard https://www.w3.org/TR/css-color-3/#svg-color',
                               default='black'),
    colorOuter: Color = Query(description='Outer Color, the value could be RGB or HEX as CSS3 standard https://www.w3.org/TR/css-color-3/#svg-color',
                              default='white'),
    colorBorder: Annotated[Union[Color, None],
                           Query(description='Border Color to use, Default = None')] = None
):
    """
    Endpoint for uploading an user picture.  

    Parameters:  
        - `quality` (FreeQualityType, Path): The quality to use.  
        - `index` (int, Query, optional): The index of the face in the picture to be used. Must be between 1 and 10. Defaults to 1.  
        - `colorCenter` (Color, Query, optional): The center color. The value could be RGB or HEX as per the CSS3 standard. Defaults to 'black'.  
        - `colorOuter` (Color, Query, optional): The outer color. The value could be RGB or HEX as per the CSS3 standard. Defaults to 'white'.  
        - `colorBorder` (Union[Color, None], Query, optional): The border color to use. Defaults to None.  
        - `picture_file` (UploadFile): The uploaded picture file.  

    Returns:
        - `FileResponse`: The response object containing the uploaded picture.
    """
    if current_user.is_active is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User disabled, please contact admin")
    if pic_file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Unsupported content type. Supported content types are 'image/jpeg' or 'image/png'",)
    if pic_file.size > 1024 * 1024 * LIMIT_SIZE_USER:     # 15MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'File size is too large, the limit is {LIMIT_SIZE_USER} MB',
        )

    newPicture = MakePicture(current_user)

    try:
        pic_path = await newPicture.make_user_picture(
            session=db,
            pic_file=pic_file,
            colorsModel=(colorCenter,
                         colorOuter),
            BorderColor=colorBorder,
            quality=quality,
            index=(index-1))

        headers = {
            'Access-Control-Expose-Headers': 'Content-Disposition',
            'picMaker-pic-url': 'this will be the url of the picture on the Quality selected'
        }
        return FileResponse(pic_path, headers=headers, media_type="image/png", filename='example.png')

    except NoFaceException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=e.message,)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="there was an error processing your request. Try again later",)


@router.post('/removebg', response_class=FileResponse, status_code=status.HTTP_201_CREATED)
async def removeBG(
    request: Request,
    picture_file: UploadFile,
    quality: Annotated[FreeQualityType, Path(title="The ID of the item to get", description='Quality to use')],
    db: Session = Depends(get_session)
    # qualityOld: FreeQualityType = Path(description='Quality to use'),
):
    """
    Remove background from an uploaded picture.

    Parameters:
        - picture_file (UploadFile): The uploaded picture file.
        - quality (FreeQualityType, optional): The quality to use. Defaults to the value specified in the path parameter.

    Returns:
        - FileResponse: The response containing the processed picture with the background removed.

    Raises:
        - HTTPException: If the number of pictures by the IP address exceeds the limit.
        - HTTPException: If the content type of the picture file is unsupported.
        - HTTPException: If the size of the picture file exceeds the limit.
        - HTTPException: If there is an error processing the picture file.
    """

    nPics_ip = FreePictureDB.get_count_ip_date(ip=request.client.host,
                                               date=datetime.now(),
                                               db=db)
    print(f'{request.client.host}: Number of pictures: {nPics_ip}')
    if nPics_ip > LIMIT_FREE_PICTURES:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f'You have reached the limit of {LIMIT_FREE_PICTURES} pictures by day. Please register your user to get unlimited pictures',)

    if picture_file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Unsupported content type. Supported content types are 'image/jpeg' or 'image/png'",)
    if picture_file.size > 1024 * 1024 * LIMIT_SIZE_FREE:     # 3MB
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'File size is too large, the limit is {LIMIT_SIZE_FREE}MB',)

    try:
        pic_path = await MakePicture.removeBG_picture(pic_file=picture_file,
                                                      quality=quality)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="there was an error processing your request. Try again later",)
    FreePictureDB.add_freePicture_toDB(Free_picture(ip=request.client.host,
                                                    quality=quality),
                                       db=db)
    headers = {
        'Access-Control-Expose-Headers': 'Content-Disposition',
        'picMaker-pics-left-day': f'{LIMIT_FREE_PICTURES - nPics_ip}'
    }
    return FileResponse(pic_path, headers=headers, media_type="image/png", filename='response.png')
