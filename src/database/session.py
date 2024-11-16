from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.models.base import Base
from src.models.tournament import Tournament

import logging
logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Create all tables in the database.
    """
    Base.metadata.create_all(bind=engine)
    logger.debug(Base.metadata.tables)
