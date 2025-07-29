from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.settings import settings_database

SQLALCHEMY_DATABASE_URL = settings_database.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# database session
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# get database generator
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
