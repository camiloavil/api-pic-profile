#FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
from fastapi.responses import JSONResponse
#SQLModel
from sqlmodel import Session
# APP
from app.models.user import User, UserNew, UserLogin, UserFB
from app.DB.db import get_session
# Python
import bcrypt

users_router = APIRouter()

@users_router.get(path="/users", 
                 response_model=list[UserFB], 
                 tags=["Users"])
def get_users():
    print("get_users")
    return "get_users"

@users_router.post(path="/new_user",
                  response_model=UserFB,
                  tags=["Users"],
                  status_code=status.HTTP_201_CREATED)
def create_user(user: UserNew = Body(...),
                session: Session = Depends(get_session)):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    
    print(str(user))
    new_user = User(name=user.name, email=user.email, pass_hash=hashed_password.decode('utf-8'))
    print(str(new_user))
    

    user_db = User.from_orm(user)
    # user_db.initDate = datetime.now()
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    print(str(user_db))
    # return JSONResponse(status_code=status.HTTP_201_CREATED,content={'message' : 'User added', 'id' : user_db.id, 'username' : user_db.name })


    return UserFB(user_id=new_user.user_id, name=user.name, email=user.email)