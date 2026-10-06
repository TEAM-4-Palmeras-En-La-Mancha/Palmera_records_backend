from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

album_genre = Table(
    "album_genre",
    Base.metadata,
    Column("album_id", Integer, ForeignKey("albums.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(80), nullable=False, unique=True)

    albums = relationship("Album", secondary="album_genre", back_populates="genres")

    def __repr__(self) -> str:
            return f"<Genre(id={self.id}, name={self.name})"
