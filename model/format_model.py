from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class Format(Base):
    __tablename__ = "formats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)

    # Relación N:M con Album a través de la tabla intermedia album_formats
    album_formats = relationship(
        "AlbumFormat",
        back_populates="format",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Format(id={self.id}, name='{self.name}')>"