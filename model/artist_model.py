from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


artist_album = Table(
    "artist_album",
    Base.metadata,
    Column("artist_id", Integer, ForeignKey("artists.id", ondelete="CASCADE"), primary_key=True),
    Column("album_id", Integer, ForeignKey("albums.id", ondelete="CASCADE"), primary_key=True),
)


class Artist(Base):

    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    bio = Column(String(500), nullable=True)

    albums = relationship(
        "Album",
        secondary="artist_album",
        back_populates="artists",
    )

    def __repr__(self) -> str:
        return f"<Artist(id={self.id}, name={self.name})"