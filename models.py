from sqlalchemy import Column, Integer, Text
from database import Base

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text)
    summary = Column(Text)