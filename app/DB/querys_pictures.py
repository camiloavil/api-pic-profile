# APP
from app.models.picture import Picture, Free_picture
# SQLModel
from sqlmodel import Session, select, func
# from sqlalchemy.exc import IntegrityError
# Python
from datetime import datetime

class PictureDB:
    def add_picture_toDB(picture: Picture, db: Session):
        try:
            db.add(picture)
            db.commit()
            db.refresh(picture)
            return picture
        except Exception as e:
            print("Error Creating a Picture register: "+str(e))
        return None

class FreePictureDB:
    def add_freePicture_toDB(picture: Free_picture, db: Session):
        try:
            db.add(picture)
            db.commit()
            db.refresh(picture)
            return picture
        except Exception as e:
            print("Error Creating a Free Picture register: "+str(e))
        return None

    def get_picture_ip(ip: str, db: Session):
        statement = select(Free_picture).where(Free_picture.ip == ip)
        freePicture_db = db.exec(statement).all()
        return freePicture_db

    def get_count_ip_date(ip: str, date: datetime, db: Session):
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
    
        record_count = db.query(func.count()).filter(Free_picture.ip == ip,
                                                    Free_picture.date >= start_date,
                                                    Free_picture.date <= end_date
                                                    ).scalar()

        return record_count
