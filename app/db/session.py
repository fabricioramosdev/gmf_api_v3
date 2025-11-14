from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
#DB_URL = os.getenv("DATABASE_URL")
DB_URL = "postgresql://gmf_lug5_user:2dq82i0Oj2KUK2919VSJZLQmIkyrcNd9@dpg-cvs7ag49c44c739r5cp0-a.oregon-postgres.render.com/gmf_lug5"

#PGPASSWORD=2dq82i0Oj2KUK2919VSJZLQmIkyrcNd9 psql -h dpg-cvs7ag49c44c739r5cp0-a.oregon-postgres.render.com -U gmf_lug5_user gmf_lug5
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
