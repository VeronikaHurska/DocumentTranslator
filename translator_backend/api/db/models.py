from datetime import datetime
from sqlalchemy import  Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from api.db.db_setup import engine

# Define the declarative base
Base = declarative_base()

# Define the table
class BotResponse(Base):
    __tablename__ = 'bot_responses'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    bot_type = Column(String(50), nullable=False)
    url_document = Column(Text, nullable=False)
    model_response = Column(Text, nullable=False)
    src_lang = Column(String(10))
    tgt_lang = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)