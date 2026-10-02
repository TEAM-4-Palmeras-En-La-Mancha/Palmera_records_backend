from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from core.database import Base


class AlbumFormat(Base):
    __tablename__ = "album_formats"

    # PK compuesta: la identidad de la fila es el par álbum + formato
    album_id = Column(Integer, ForeignKey("albums.id"), primary_key=True)
    format_id = Column(Integer, ForeignKey("formats.id"), primary_key=True)

    # Atributos propios de la edición
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    album = relationship("Album", back_populates="album_formats")
    format = relationship("Format", back_populates="album_formats")