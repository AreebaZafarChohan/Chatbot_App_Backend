from sqlalchemy import Column, String, Integer
from app.db.connection import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    status = Column(String, default="pending")  
