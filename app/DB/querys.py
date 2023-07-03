# APP
from app.models.user import User
from app.DB.db import get_session
from app.DB.db import engine
# SQLModel
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from fastapi import Depends

def add_user_to_db(user: User,session: Session):
    """
    Add a user to the database.

    Parameters:
    - user: An instance of the User class.

    Returns:
    - The added user if successful, None otherwise.
    """
    try:
        # with Session(engine) as session:
        session.add(user)
        session.commit()
        return user
    except IntegrityError as e:
        print("Error: User already exists:"+str(e))
    except Exception as e:
        print("Error Creating User:"+str(e))
    return None

def get_userDB_by_email(username: str, session: Session):
    """
    Retrieves a user's database object by their email address.

    :param username: A string representing the email address of the user.
    :type username: str

    :return: The database object representing the user.
    :rtype: User
    """
    statement = select(User).where(User.email == username)
    user_db = session.exec(statement).first()
    return user_db
    # with Session(engine) as session:
    #     statement = select(User).where(User.email == username)
    #     user_db = session.exec(statement).first()
    # return user_db