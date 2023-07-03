#FastAPI
from fastapi import APIRouter, status, HTTPException
from fastapi import Depends, Query, Path
from fastapi.responses import JSONResponse
# SQLModel
from sqlmodel import Session, select
# Python
from pydantic import EmailStr
from typing import Annotated
from typing import List
from uuid import UUID
# APP
from app.models.user import User, UserFB
from app.DB.db import get_session
from app.DB.querys import get_userDB_by_email
from app.security.secureuser import get_current_user

router = APIRouter()

@router.get(path='/allusers', 
            response_model= List[UserFB], 
            status_code=status.HTTP_200_OK
            )
def get_users(current_user: Annotated[User, Depends(get_current_user)],
            #   offset: int = Query(description='Offset of the query',default=1,ge=1),
              limit: int = Query(description='Limit of data per request',default=100, lte=100), 
              session: Session = Depends(get_session)) -> dict:
    """
    Retrieve all users if the current user is an admin. Returns a list of UserFB objects.
    
    Args:
        current_user (Annotated[User, Depends(get_current_user)]): The current user requesting data.
        limit (int): Limit of data per request. Defaults to 100.
        session (Session): A SQLAlchemy session object.
        
    Returns:
        A list of UserFB objects.
    
    Raises:
        HTTPException: If the current user is not an admin.
    """
    if(current_user.userType != 'admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User Unauthorized")
    users = session.exec(select(User).limit(limit)).all()
    # users = session.exec(select(User).offset(offset).limit(limit)).all() #Doesn't Work check it
    return [UserFB(**user.dict()) for user in users]


@router.get(path='/getuser/email/{email}', 
            response_model=UserFB, 
            status_code=status.HTTP_200_OK
            )
def getUserbyEmail(current_user: Annotated[User, Depends(get_current_user)],
                   email: EmailStr = Path(description='e-mail of the user to get', 
                                          example='user@example.com'), 
                    session: Session = Depends(get_session)) -> User:
    """
    Retrieves a user from the database based on their email address.
    
    Args:
        current_user (Annotated[User, Depends(get_current_user)]): The currently authenticated user.
        email (EmailStr): The email address of the user to retrieve.
        session (Session): The database session to use.
    
    Returns:
        User: The requested user object.
    
    Raises:
        HTTPException: If the current user is not an admin, or if the requested user is not found.
    """

    if(current_user.userType != 'admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User Unauthorized")

    print(f'User id:{email}')
    user = get_userDB_by_email(email,session=session)
    if user is not None:
        return UserFB(**user.dict())
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f'Error. User e-mail: {email} Not found')


@router.get(path='/getuser/{uuid}', 
            response_model=UserFB, 
            status_code=status.HTTP_200_OK)
def getUserbyUUID(current_user: Annotated[User, Depends(get_current_user)],
                  uuid: UUID = Path(description='UUID of the user to get'), 
                  session: Session = Depends(get_session)) -> User:
    """
    Retrieves a user from the database by UUID.

    Args:
        current_user (Annotated[User, Depends(get_current_user)]): The current user making the request.
        uuid (UUID, optional): The UUID of the user to retrieve. Defaults to Path(description='UUID of the user to get').
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        User: The user object retrieved from the database.

    Raises:
        HTTPException: If the current user is not an admin or if the requested user is not found in the database.
    """

    if(current_user.userType != 'admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User Unauthorized")
    user = session.get(User, uuid)
    if user is not None:
        return UserFB(**user.dict())
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f'Error. User uuid:{uuid} Not found')

@router.delete(path='/deluser/{uuid}',
               response_model=dict,
               status_code=status.HTTP_200_OK)
def delete_user(current_user: Annotated[User, Depends(get_current_user)],
                uuid: UUID = Path(description="User ID to delete"),
                session: Session = Depends(get_session)) -> dict:
    
    if(current_user.userType != 'admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User Unauthorized")
    
    user = session.get(User, uuid)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Error. User uuid:{uuid} Not found')
    session.delete(user)
    session.commit()
    return JSONResponse(content={'message':f'User uuid:{uuid} deleted'},
                        status_code=status.HTTP_200_OK)
