#FastAPI
from fastapi import APIRouter, status, HTTPException
from fastapi import Depends, Body, Form
from fastapi.responses import JSONResponse
# SQLModel
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
#Python
from typing import Annotated
from pydantic import SecretStr
# APP
from app.models.user import User, UserCreate, UserUpdate, UserFB
from app.DB.db import get_session
from app.security.secureuser import verify_password, get_password_hash, get_current_user

router = APIRouter()

@router.post(path='/newuser', 
                   response_model=UserFB, 
                   status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate = Body(), 
                session: Session = Depends(get_session)) -> dict:
    """
    Creates a new user and adds it to the database. Accepts a user object as a Body parameter in the request. 
    The function returns a dictionary representation of the newly created user
    If the user already exists, it raises an HTTPException with a status code of 409. 
    If there is an internal error while creating the user, it raises an HTTPException with a status code of 400. 

    :param user: UserCreate object. Required. 
    :param session: Session object. Required.
    :return: A dictionary representation of the newly created user
    :raises HTTPException 409: If the user already exists.
    :raises HTTPException 400: If there is an internal error while creating the user.
    """
    userDict = user.dict()
    userDict.update({'pass_hash' : get_password_hash(user.password.get_secret_value())})

    try:
        user_db = User.from_orm(User(**userDict))
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        # print(str(user_db))
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    except Exception as e:
        print("Error Creating User:"+str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Internal Error")
    return UserFB(**user_db.dict())

@router.get(path="/myuser",
            response_model=UserFB,
            status_code=status.HTTP_200_OK
            )
async def info_User(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get information about the current user.

    :return: UserFB - Information about the current user
    """
    return UserFB(**current_user.dict())

# @router.put(path='/myuser/{id}', tags=['users'],response_model=ResponseModel, status_code=status.HTTP_200_OK)
@router.put(path='/myuser', 
                  response_model= UserFB, 
                  status_code=status.HTTP_200_OK)
def update_user(current_user: Annotated[User, Depends(get_current_user)],
                newData: UserUpdate = Body(),
                session: Session = Depends(get_session)) -> dict:
    """
    Updates the user information for the user with the given user ID. 

    Args:
        current_user (Annotated[User, Depends(get_current_user)]): The user making the request.
        newData (UserUpdate = Body()): The new user information to update.

    Returns:
        A dictionary containing the updated user information.
    """
    newData_dict = newData.dict(exclude_unset=True)
    user_db = session.get(User,current_user.user_id)
    for key, value in newData_dict.items():
        # print(f'key:{key} value:{value}')
        setattr(user_db,key,value)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return UserFB(**user_db.dict())
    return JSONResponse(content={'message':f'User id:{id} updated correctly'},status_code=status.HTTP_200_OK)

@router.delete(path='/myuser',
               response_model=dict,
               status_code=status.HTTP_200_OK)
def disable_user(current_user: Annotated[User, Depends(get_current_user)],
                session: Session = Depends(get_session)) -> dict:
    """
    Deletes a user from the database by setting their 'is_active' attribute to False.
    
    Args:
        current_user (Annotated[User, Depends(get_current_user)]): The current user making the request.
        session (Session, optional): The SQLAlchemy session object. Defaults to Depends(get_session).
        
    Returns:
        dict: A JSON response containing a message indicating the user was deleted, and a 200 HTTP status code.
    """
    user_db = session.get(User, current_user.user_id)
    setattr(user_db,'is_active',False)
    session.commit()
    return JSONResponse(content={'message':f'User id:{str(current_user.user_id)} disabled'},status_code=status.HTTP_200_OK)

@router.put(path='/myuser/changepassword', 
            response_model= dict,
            status_code=status.HTTP_200_OK)
def update_password_user(current_user: Annotated[User, Depends(get_current_user)],
                         actual_password: SecretStr = Form(min_length=8, max_length=35),
                         new_password: SecretStr = Form(min_length=8, max_length=35),
                         session: Session = Depends(get_session)) -> dict:
    """
    Updates the password of the current user.

    Args:
        current_user (Annotated[User, Depends(get_current_user)]): The current user.
        actual_password (SecretStr, optional): The current password. Defaults to Form(min_length=8, max_length=35).
        new_password (SecretStr, optional): The new password. Defaults to Form(min_length=8, max_length=35).
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        dict: A JSON response with a message and status code.
    Raises:
        HTTPException: If there is an error updating the password or if the actual password is incorrect.
    """
    if (verify_password(actual_password.get_secret_value(), current_user.pass_hash)):
        try:
            user_db = session.get(User,current_user.user_id)
            setattr(user_db,'pass_hash',get_password_hash(new_password.get_secret_value()))
            session.add(user_db)
            session.commit()
            session.refresh(user_db)
            return JSONResponse(content={'message':f'User id:{str(current_user.user_id)} password updated'},
                                status_code=status.HTTP_200_OK)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There is an error updating the password")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect actual password")

