from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from model.album_format_model import AlbumFormat
from model.album_model import Album
from model.format_model import Format
from schema.album_format_schema import AlbumFormatCreate, AlbumFormatUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[AlbumFormat]:

    try:
        return db.query(AlbumFormat).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching album formats: {str(error)}"
        )


def get_by_id(db: Session, album_id: int, format_id: int) -> AlbumFormat:

    try:
        edition = db.query(AlbumFormat).filter(
            AlbumFormat.album_id == album_id,
            AlbumFormat.format_id == format_id
        ).first()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching album format: {str(error)}"
        )

    if not edition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Album {album_id} does not exist in format {format_id}"
        )
    return edition


def create_album_format(
    db: Session,
    album_format_data: AlbumFormatCreate
) -> AlbumFormat:

    album = db.query(Album).filter(Album.id == album_format_data.album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Album with id {album_format_data.album_id} not found"
        )

    format_row = db.query(Format).filter(
        Format.id == album_format_data.format_id
    ).first()
    if not format_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format with id {album_format_data.format_id} not found"
        )

    existing = db.query(AlbumFormat).filter(
        AlbumFormat.album_id == album_format_data.album_id,
        AlbumFormat.format_id == album_format_data.format_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Album {album_format_data.album_id} already exists in format {album_format_data.format_id}"
        )

    new_edition = AlbumFormat(
        album_id=album_format_data.album_id,
        format_id=album_format_data.format_id,
        price=album_format_data.price,
        stock=album_format_data.stock
    )

    try:
        db.add(new_edition)
        db.commit()
        db.refresh(new_edition)
        return new_edition
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in creating album format: {str(error)}"
        )


def update_album_format(
    db: Session,
    album_id: int,
    format_id: int,
    album_format_data: AlbumFormatUpdate
) -> AlbumFormat:

    edition = get_by_id(db, album_id, format_id)

    update_data = {
        field: value
        for field, value in album_format_data.model_dump(exclude_unset=True).items()
        if value is not None
    }

    for field, value in update_data.items():
        setattr(edition, field, value)

    try:
        db.commit()
        db.refresh(edition)
        return edition
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in updating album format ({album_id}, {format_id}): {str(error)}"
        )


def delete_album_format(db: Session, album_id: int, format_id: int) -> None:

    edition = get_by_id(db, album_id, format_id)

    try:
        db.delete(edition)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting album format ({album_id}, {format_id}): {str(error)}"
        )