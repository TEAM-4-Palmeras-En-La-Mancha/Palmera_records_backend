from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from model.genre_model import Genre
from schema.genre_schema import GenreCreate, GenreUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Genre]:
    try:
        return db.query(Genre).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in getting genres {str(error)}"
        )


def get_by_id(db: Session, genre_id: int) -> Genre:
    genre = db.query(Genre).filter(Genre.id == genre_id).first()

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Genre with id {genre_id} not found"
        )

    return genre


def create_genre(db: Session, genre_data: GenreCreate) -> Genre:
    existing = db.query(Genre).filter(Genre.name == genre_data.name).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Genre with name '{genre_data.name}' already exists"
        )

    new_genre = Genre(name=genre_data.name)

    try:
        db.add(new_genre)
        db.commit()
        db.refresh(new_genre)
        return new_genre
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Genre with name '{genre_data.name}' already exists"
        )
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in creating genre {str(error)}"
        )


def update_genre(db: Session, genre_id: int, genre_data: GenreUpdate) -> Genre:
    genre = get_by_id(db, genre_id)

    if genre_data.name is None:
        return genre

    duplicate = db.query(Genre).filter(
        Genre.name == genre_data.name,
        Genre.id != genre_id
    ).first()
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Genre with name '{genre_data.name}' already exists"
        )

    genre.name = genre_data.name

    try:
        db.commit()
        db.refresh(genre)
        return genre
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Genre with name '{genre_data.name}' already exists"
        )
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in updating genre {str(error)}"
        )


def delete_genre(db: Session, genre_id: int) -> None:
    genre = get_by_id(db, genre_id)

    try:
        db.delete(genre)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting genre {str(error)}"
        )