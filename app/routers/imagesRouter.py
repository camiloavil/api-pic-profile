# FastAPI
from fastapi import APIRouter, status, HTTPException, UploadFile
from fastapi import File
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
# ProfilePicMaker
from ProfilePicMaker.app.models.pictures import BigPic
from ProfilePicMaker.app.models.colors import Color
# from app.models.pictures import BigPic
# Python
import tempfile

router = APIRouter()

@router.post('/uploadPicture',
    # response_model=UploadFile, 
    status_code=status.HTTP_201_CREATED)
async def upload_pic(pic_file: UploadFile = File(...)):
    unsuported_exception = HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported content type. Supported content types are 'image/jpeg'",
    )
    if pic_file.content_type not in ["image/jpeg", "image/png"]:
        raise unsuported_exception
    if pic_file.size > 1024 * 1024 * 3:     # 3MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size is too large",
        )
    # temp_dir = tempfile.TemporaryDirectory()
    # colorborder: Annotated[str, typer.Option(help="Color to use for the border, Default = None")] = None
    Acolor = Color.get_color_rgb('white')
    Bcolor = Color.get_color_rgb('black')
    # BorderColor = None if colorborder is None else Color.get_color_rgb(colorborder)
    BorderColor = None 
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix=".jpg") as temp_file:
            # Save the uploaded file to the temporary file
            with open(temp_file.name, "wb") as f:
                f.write(await pic_file.read())
            print(temp_file.name)
            faces = BigPic(temp_file.name).get_faces()
            if(len(faces) == 0):
                return {"error": "No Faces detected"}
            print(len(faces))
            for face in faces:
                face.resize(300)
                face.removeBG()
                face.addBG(Acolor,Bcolor)
                face.set_contour()
                if BorderColor is not None:
                    face.setBorder(BorderColor)
                face.setBlur(30)
                # face.show()
                face.save(tol= 5)       # save the pic on a temp file during 5 sec
                return FileResponse(face.get_path())
            # The temporary file will be deleted automatically when closed

            # Do your processing here

    except Exception as e:
        return {"error": str(e)}

    
    return {"filename": pic_file.filename,
            "format": pic_file.content_type,
            "size": pic_file.size,
            "sizeInBytes": round(len(pic_file.file.read())/1024,ndigits=2),
            "temp_file": str(temp_file.name),}
