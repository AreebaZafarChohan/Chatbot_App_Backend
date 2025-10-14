from sqlalchemy import Column, String
from app.db.connection import Base

class MemoryFact(Base):
    __tablename__ = "memory_facts"

    user_id = Column(String, primary_key=True)
    key = Column(String, primary_key=True)
    value = Column(String)
