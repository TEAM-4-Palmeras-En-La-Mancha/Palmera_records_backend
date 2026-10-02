from typing import List
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from model.artist_model import Artist
from model.album_model import Album
from schema.artist_schema import ArtistCreate, ArtistUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Artist]:
    try:
        return db.query(Artist).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in getting artists {str(error)}"
        )


def get_by_id(db: Session, artist_id: int) -> Artist:
    try:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in getting artist {str(error)}"
        )
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {artist_id} not found"
        )
    return artist


def create_artist(db: Session, artist_data: ArtistCreate) -> Artist:
    new_artist = Artist(
        name=artist_data.name,
        bio=artist_data.bio
    )
    try:
        db.add(new_artist)
        db.commit()
        db.refresh(new_artist)
        return new_artist
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in creating artist {str(error)}"
        )


def update_artist(db: Session, artist_id: int, artist_data: ArtistUpdate) -> Artist:
    artist = get_by_id(db=db, artist_id=artist_id)
    update_data = artist_data.model_dump(exclude_unset=True)
    try:
        for field, value in update_data.items():
            setattr(artist, field, value)
        db.commit()
        db.refresh(artist)
        return artist
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in updating artist {str(error)}"
        )


def delete_artist(db: Session, artist_id: int) -> dict:
    artist = get_by_id(db=db, artist_id=artist_id)
    try:
        # Borrado en cascada manual: elimina los álbumes del artista
        for album in list(artist.albums):
            db.delete(album)
        db.delete(artist)
        db.commit()
        return {"detail": f"Artist with id {artist_id} deleted successfully"}
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting artist {str(error)}"
        )

    