from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from model.format_model import Format
from schema.format_schema import FormatCreate, FormatUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Format]:

    try:
        return db.query(Format).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching formats: {str(error)}"
        )


def get_by_id(db: Session, format_id: int) -> Format:

    try:
        format_row = db.query(Format).filter(Format.id == format_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching format {format_id}: {str(error)}"
        )

    if not format_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format with id {format_id} not found"
        )
    return format_row


def create_format(db: Session, format_data: FormatCreate) -> Format:

    existing = db.query(Format).filter(Format.name == format_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A format with name '{format_data.name}' already exists"
        )

    new_format = Format(
        name=format_data.name,
        description=format_data.description
    )

    try:
        db.add(new_format)
        db.commit()
        db.refresh(new_format)
        return new_format
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in creating format: {str(error)}"
        )


def update_format(db: Session, format_id: int, format_data: FormatUpdate) -> Format:

    format_row = get_by_id(db, format_id)

    update_data = format_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        duplicate = db.query(Format).filter(
            Format.name == update_data["name"],
            Format.id != format_id
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A format with name '{update_data['name']}' already exists"
            )

    for field, value in update_data.items():
        setattr(format_row, field, value)

    try:
        db.commit()
        db.refresh(format_row)
        return format_row
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in updating format {format_id}: {str(error)}"
        )


def delete_format(db: Session, format_id: int) -> None:

    format_row = get_by_id(db, format_id)

    try:
        db.delete(format_row)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting format {format_id}: {str(error)}"
        )