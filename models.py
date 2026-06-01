import json

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)

    original_text = Column(Text)
    summary = Column(Text)
    content_type = Column(String)
    
    agent_output = Column(Text)  # store as JSON string

    created_at = Column(DateTime, default=datetime.utcnow)