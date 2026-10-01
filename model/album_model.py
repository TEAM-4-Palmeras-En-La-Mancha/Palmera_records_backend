from sqlalchemy import Column, Integer,ForeignKey, String, Enum
from sqlalchemy.orm import relationship

from core.database import Base
from enums.genres_enum import Genres

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False, unique=True)
    release_year = Column(Integer, nullable=False)
    genre = Column(Enum(Genres),nullable=False)
    cover_image_url= Column(String,nullable=True)
    label_id= Column(Integer,ForeignKey("record_labels.id"),nullable=False)

    label = relationship(
      "Labels",
      back_populates="Albums"
    )

    album_formats= relationship(
        "AlbumFormat",
        back_populates="Album"
    )