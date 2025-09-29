// payment-gateway/database.py
"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./payment_gateway.db')

engine = create_engine(DATABASE_URL, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialize database tables"""
    import models
    Base.metadata.create_all(bind=engine)
