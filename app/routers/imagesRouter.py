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
from app.security.secureuser import get_current_user
# Python
from typing import Annotated, Union
import tempfile

router = APIRouter()

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
    # if pic_file.content_type not in ["image/jpeg", "image/png"]:
    if pic_file.content_type not in ("image/jpeg",):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported content type. Supported content types are 'image/jpeg'",
            )
    if pic_file.size > 1024 * 1024 * 3:     # 3MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size is too large",
        )
    # temp_dir = tempfile.TemporaryDirectory()
    # colorborder: Annotated[str, typer.Option(help="Color to use for the border, Default = None")] = None
    Acolor = Color.get_color_rgb(colorA.value)
    Bcolor = Color.get_color_rgb(colorB.value)
    BorderColor = None if border is None else Color.get_color_rgb(border.value)
    # print(str(BorderColor))
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
            faces[index].resize(300)
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
