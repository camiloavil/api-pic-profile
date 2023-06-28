#FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
# from fastapi.responses import JSONResponse
#SQLModel
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
# APP
from app.models.user import User, UserNew, UserFB
from app.DB.db import get_session
from app.security.userschema import get_current_user, get_password_hash
# Python
from typing import Annotated

users_router = APIRouter()

@users_router.get(path="/myuser/",
                  response_model=UserFB,
                  tags=["Users"])
async def info_User(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get information about the current user.

    :return: UserFB - Information about the current user
    """
    return UserFB(**current_user.dict())

@users_router.get(path="/allusers", 
                 response_model=list[UserFB], 
                 tags=["Users"])
def get_allusers(session: Session = Depends(get_session)):
    all_users = session.query(User).all()
    all_users = [UserFB(**user.dict()) for user in all_users]
    
    return all_users

@users_router.post(path="/new_user",
                  response_model=UserFB,
                  tags=["Users"],
                  status_code=status.HTTP_201_CREATED)
def create_user(user: UserNew = Body(...),
                session: Session = Depends(get_session)):
    user_dict = user.dict()
    user_dict.update({"pass_hash": get_password_hash(user.password.get_secret_value())})
    new_user = User(**user_dict)
    
    try:
        user_db = User.from_orm(new_user)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        print(str(user_db))
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    except Exception as e:
        print("Error Creating User:"+str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return UserFB(user_id=new_user.user_id, name=user.name, email=user.email)
    # return JSONResponse(status_code=status.HTTP_201_CREATED,content={'message' : 'User added', 'id' : user_db.id, 'username' : user_db.name })


