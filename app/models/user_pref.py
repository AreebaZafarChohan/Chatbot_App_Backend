from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.db.connection import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    preference: Mapped[str] = mapped_column(String)
