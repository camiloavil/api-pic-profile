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
from sqlalchemy.exc import IntegrityError

users_router = APIRouter()

@users_router.get(path="/users", 
                 response_model=list[UserFB], 
                 tags=["Users"])
def get_users(session: Session = Depends(get_session)):
    print("get_users")
    all_users = session.query(User).all()
    print(all_users)
    all_users = [UserFB(name=user.name, email=user.email, user_id=user.user_id) for user in all_users]
    print(all_users)
    
    return all_users

@users_router.post(path="/new_user",
                  response_model=UserFB,
                  tags=["Users"],
                  status_code=status.HTTP_201_CREATED)
def create_user(user: UserNew = Body(...),
                session: Session = Depends(get_session)):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.get_secret_value().encode('utf-8'), salt)
    new_user = User(name=user.name, email=user.email, pass_hash=hashed_password.decode('utf-8'))
    
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

@users_router.post(path="/login",
                  response_model=UserFB,
                  tags=["Users"],
                  status_code=status.HTTP_200_OK)
def login(user: UserLogin = Body(...),
          session: Session = Depends(get_session)):
    user_db = session.query(User).filter(User.email == user.email).first()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = bcrypt.checkpw(user.password.get_secret_value().encode('utf-8'), user_db.pass_hash.encode('utf-8'))
    if result:
        return UserFB(user_id=user_db.user_id, name=user_db.name, email=user_db.email)
        # return JSONResponse(status_code=status.HTTP_200_OK,content={'message' : 'Login Success'})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")