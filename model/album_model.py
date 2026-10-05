from sqlalchemy import Column, Integer,ForeignKey, String
from sqlalchemy.orm import relationship
from core.database import Base

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    cover_image_url= Column(String,nullable=True)
    label_id= Column(Integer,ForeignKey("record_labels.id"),nullable=False)

    record_label = relationship(
      "RecordLabel",
      back_populates="albums"
    )

    album_formats= relationship(
        "AlbumFormat",
        back_populates="album",
      cascade="all, delete-orphan"
    )
    artists = relationship(
        "Artist",
        secondary="artist_album",
        back_populates="albums",
    )

    genres = relationship(
    "Genre",
    secondary="album_genre",
    back_populates="albums",
  )