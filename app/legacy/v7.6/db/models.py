from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import func

from datetime import datetime

from app.db.database import Base

class Summary(Base):

    __tablename__ = "summaries"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    original_text = Column(
        Text
    )

    summary = Column(
        Text
    )

    content_type = Column(
        String,
        default="General Content"
    )

    agent_output = Column(
        Text
    )

    execution_plan = Column(Text)

    execution_metadata = Column(Text)

    primary_intent = Column(String)

    agent_count = Column(Integer)

    execution_time = Column(Float)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )