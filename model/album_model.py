from sqlalchemy import Column, Integer,ForeignKey, String, Enum
from sqlalchemy.orm import relationship

from core.database import Base
from enums.genres_enum import Genres

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    genre = Column(Enum(Genres),nullable=False)
    cover_image_url= Column(String,nullable=True)
    label_id= Column(Integer,ForeignKey("record_labels.id"),nullable=False)

    label = relationship(
      "RecordLabel",
      back_populates="Albums"
    )

    album_formats= relationship(
        "AlbumFormat",
        back_populates="Album",
      cascade="all, delete-orphan"
    )
    artists = relationship(
        "Artist",
        secondary="artist_album",
        back_populates="albums",
    )