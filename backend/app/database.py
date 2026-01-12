from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI.__str__())

Session = sessionmaker(engine)