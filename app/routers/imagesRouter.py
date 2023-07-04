# FastAPI
from fastapi import APIRouter, status, HTTPException, UploadFile
from fastapi import File
# ProfilePicMaker
from ProfilePicMaker.app.models.pictures import BigPic
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
    print(pic_file.content_type)
    if pic_file.content_type not in ["image/jpeg", "image/png"]:
        raise unsuported_exception
    if pic_file.size > 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size is too large",
        )
    temp_dir = tempfile.TemporaryDirectory()
    
    return {"filename": pic_file.filename,
            "format": pic_file.content_type,
            "size": pic_file.size,
            "sizeInBytes": round(len(pic_file.file.read())/1024,ndigits=2),
            "temp_dir": str(temp_dir),}
