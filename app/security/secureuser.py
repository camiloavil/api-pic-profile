# FastAPI
from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# SQLModel
from sqlmodel import Session
# PassLib
from passlib.context import CryptContext
# Jose
from jose import jwt, JWTError
# Pyhon
from typing import Annotated, Union
from datetime import datetime, timedelta
# APP
from app.security import URL_USER_LOGIN, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.DB.querys import get_userDB_by_email
from app.DB.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_User_scheme = OAuth2PasswordBearer(tokenUrl=URL_USER_LOGIN)

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str):
    """
    Verify if a given plain password matches a hashed password using the PyJWT password context.

    :param plain_password: A string representing the plain password to be verified.
    :type plain_password: str
    :param hashed_password: A string representing the hashed password to compare with.
    :type hashed_password: str
    :return: A boolean indicating if the plain password matches the hashed password.
    :rtype: bool
    """
    return pwd_context.verify(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    """
    Generates a hash of the input string password using the password hashing framework 
    pwd_context. 

    :param password: The password string to hash.
    :type password: str
    :return: Hashed password string.
    :rtype: str
    """
    return pwd_context.hash(password.encode('utf-8'))

def get_current_user(token: Annotated[str, Depends(oauth2_User_scheme)], 
                           session: Session = Depends(get_session)):
    """
    Asynchronously retrieves a user object from the database based on the provided bearer token.

    :param token: The bearer token used to authenticate the request.
    :type token: Annotated[str, Depends(oauth2_User_scheme)]
    :raises HTTPException: If the token could not be validated.
    :return: A User object representing the authenticated user.
    :rtype: User
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_userDB_by_email(username=username,session=session)
    if user is None:
        raise credentials_exception
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    Creates an access token using input data and an optional expiration time delta.

    Args:
        data (dict): The data to be encoded in the access token.
        expires_delta (Union[timedelta, None], optional): The expiration time delta. Defaults to None.

    Returns:
        bytes: The encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post(path="/"+URL_USER_LOGIN,
                  response_model=dict,
                  tags=["Users"])
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
          session: Session = Depends(get_session)):
    """
    Authenticates a user by checking the validity of their provided credentials 
    and returns an access token if successful.

    :param form_data: The OAuth2PasswordRequestForm containing the user's login 
                      credentials.
    :type form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    :raises HTTPException: If the user's credentials are invalid.
    :return: A dictionary containing the user's access token and its bearer type.
    :rtype: Dict[str, str]
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    user_db = get_userDB_by_email(form_data.username, session)

    if user_db is None:
        raise credentials_exception
    if not verify_password(form_data.password, user_db.pass_hash):
        raise credentials_exception
    access_token = create_access_token(data={"sub": user_db.email}, 
                                       expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}