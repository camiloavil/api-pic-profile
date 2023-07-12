# APP
from app.models import MyModels
# SQLModel
from sqlmodel import Session, create_engine
# Python
import os

#Filename of sqlite DB
SQLITE_FILENAME = 'DB.sqlite'                       
# BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

#set location of DB File on the same folder of this file
# DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR,SQLITE_FILENAME)}?check_same_thread=False' 
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
# engine = create_engine(DATABASE_URL, echo = False)  
engine = create_engine(f'sqlite:///{os.path.join(BASE_DIR,SQLITE_FILENAME)}', 
                       connect_args={'check_same_thread': False}, 
                       echo=False)

def create_db_table():
    MyModels.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
