from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from model.album_model import Album
from model.record_labels_model import RecordLabel
from schema.album_schema import AlbumCreate, AlbumUpdate

def get_all(db: Session,
            skip: int =0,
            limit: int= 100
)-> List[Album]:
    
    try:
        return db.query(Album).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in getting albums: {str(error)}"
        )

def get_by_id(
    db: Session,
    album_id: int
) -> Album:

    try:
        album = db.query(Album).filter(
            Album.id == album_id
        ).first()

        if album is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Album not found"
            )

        return album

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in getting album: {str(error)}"
        )    
def create_albums(
        db: Session,
        album_data: AlbumCreate
) -> Album:
    
    recordLabel = db.query(RecordLabel).filter(
    RecordLabel.id == album_data.label_id
    ).first()


    if recordLabel is None:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found"
        )

    newAlbum = Album(
        title = album_data.title,
        release_year = album_data.release_year,
        genre = album_data.genre,
        cover_image_url= album_data.cover_image_url,
        label_id= album_data.label_id
    )

    try:
        db.add(newAlbum)
        db.commit()
        db.refresh(newAlbum)

        return newAlbum
    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in creating album: {str(error)}"
        )


def update_album(
            db: Session,
            album_id: int,
            album_data: AlbumUpdate
) -> Album:
    album = db.query(Album).filter(
        Album.id == album_id
    ).first()

    if album is None:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )
    if album_data.label_id is not None:
        recordLabel = db.query(RecordLabel).filter(
            RecordLabel.id == album_data.label_id
        ).first()

        if recordLabel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record label not found"
            )

        album.label_id = album_data.label_id

    if album_data.title is not None:
        album.title = album_data.title
    if album_data.genre is not None:
        album.genre = album_data.genre
    if album_data.release_year is not None:
        album.release_year = album_data.release_year
    if album_data.cover_image_url is not None:
        album.cover_image_url = album_data.cover_image_url

    try:
        db.commit()
        db.refresh(Album)

        return album

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in updating album: {str(error)}"
        )

def delete_Album(db: Session, album_id:int)-> None:
    album = db.query(Album).filter(
        Album.id == album_id
    ).first()
    if album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )
    try:
        db.delete(album)
        db.commit()

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting album: {str(error)}"
        )