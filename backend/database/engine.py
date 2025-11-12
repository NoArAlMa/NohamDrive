from sqlmodel import create_engine, SQLModel
from core.config import settings



DB_URL = settings.database_url

engine = create_engine(DB_URL, echo=settings.DEBUG)  


def init_db():
    SQLModel.metadata.create_all(engine)
