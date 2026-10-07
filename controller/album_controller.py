from typing import List
from model.artist_model import Artist
from model.genre_model import Genre
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from model.album_model import Album
from model.record_labels_model import RecordLabel
from model.artist_model import Artist
from schema.album_schema import AlbumCreate, AlbumUpdate
from service import cloudinary_service

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
        album_data: AlbumCreate,
        cover_image: UploadFile | None = None
) -> Album:
    
    recordLabel = db.query(RecordLabel).filter(
    RecordLabel.id == album_data.label_id
    ).first()


    if recordLabel is None:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found"
        )
    
    image_url =None
    image_id = None
    if cover_image is not None:
        result = cloudinary_service.upload_image(
            cover_image.file,
            folder="palmeras_records/albums"
        )
        image_url = result["secure_url"]
        image_id = result["public_id"]

    genres = db.query(Genre).filter(
        Genre.id.in_(album_data.genre_ids)
    ).all()

    if len(genres) != len(set(album_data.genre_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )

    artist = db.query(Artist).filter(
        Artist.id.in_(album_data.artist_ids)
    ).all()

    if len(artist) != len(set(album_data.artist_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    newAlbum = Album(
        title = album_data.title,
        release_year = album_data.release_year,
        cover_image_url= image_url,
        cover_image_public_id = image_id,
        label_id= album_data.label_id
    )

    if album_data.artist_ids:
        artists = db.query(Artist).filter(Artist.id.in_(album_data.artist_ids)).all()
        newAlbum.artists = artists

    newAlbum.genres = genres
    newAlbum.artists = artist
    
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
            album_data: AlbumUpdate,
            cover_image:UploadFile | None = None
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
    if album_data.genre_ids is not None:
        genres = db.query(Genre).filter(
            Genre.id.in_(album_data.genre_ids)
        ).all()

        if len(genres) != len(set(album_data.genre_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Genre not found"
            )

        album.genres = genres
    if album_data.artist_ids is not None:
        artists = db.query(Artist).filter(
            Artist.id.in_(album_data.artist_ids)
        ).all()

        if len(artists) != len(set(album_data.artist_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist not found"
            )

        album.artists = artists
    if album_data.release_year is not None:
        album.release_year = album_data.release_year
    if cover_image is not None:
        if album.cover_image_public_id:
            cloudinary_service.delete_image(
                album.cover_image_public_id
            )

        result = cloudinary_service.upload_image(
            cover_image.file,
            folder="palmeras_records/albums"
        )

        album.cover_image_url = result["secure_url"]
        album.cover_image_public_id = result["public_id"]

    if album_data.artist_ids is not None:
        artists = db.query(Artist).filter(Artist.id.in_(album_data.artist_ids)).all()
        album.artists = artists

    try:
        db.commit()
        db.refresh(album)

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
        if album.cover_image_public_id:
            cloudinary_service.delete_image(
                album.cover_image_public_id
            )

        db.delete(album)
        db.commit()

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting album: {str(error)}"
        )

def get_by_record_label(
    db: Session,
    label_id: int
) -> List[Album]:

    try:
        return (
            db.query(Album)
            .filter(Album.label_id == label_id)
            .all()
        )

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching albums: {str(error)}"
        )