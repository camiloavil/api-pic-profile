from fastapi import APIRouter, status, File, UploadFile

router = APIRouter()

@router.post('/uploadFile', tags=['files'], 
                   #response_model=ResponseModel, 
                   status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a file to the server.

    Args:
        file: An instance of UploadFile containing information about the file to be uploaded.

    Returns:
        A dictionary containing the filename, format, and size of the uploaded file.

    Raises:
        HTTPException: If there is an error during file upload.

    """
    return {"filename": file.filename,
            "format": file.content_type,
            "size": file.size}
