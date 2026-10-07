from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base


class RecordLabel(Base):
    __tablename__ = "record_labels"


    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    website = Column(String(255), nullable=True)

    albums = relationship("Album", back_populates="record_label", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RecordLabel(id={self.id}, name='{self.name}', country='{self.country}')>"