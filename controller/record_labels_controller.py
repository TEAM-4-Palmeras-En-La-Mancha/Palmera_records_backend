from typing import List
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from model.record_labels_model import RecordLabel
from schema.record_labels_schema import RecordLabelCreate, RecordLabelUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[RecordLabel]:

    try:
        return db.query(RecordLabel).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching record labels: {str(error)}"
        )


def get_by_id(db: Session, label_id: int) -> RecordLabel:

    try:
        label = db.query(RecordLabel).filter(RecordLabel.id == label_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching record label: {str(error)}"
        )

    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record label with id {label_id} not found"
        )
    return label


def create_record_label(db: Session, label_data: RecordLabelCreate) -> RecordLabel:

    new_label = RecordLabel(
        name=label_data.name,
        country=label_data.country,
        website=label_data.website
    )

    try:
        db.add(new_label)
        db.commit()
        db.refresh(new_label)
        return new_label
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in creating record label: {str(error)}"
        )


def update_record_label(db: Session, label_id: int, label_data: RecordLabelUpdate) -> RecordLabel:

    label = get_by_id(db, label_id)

    update_data = label_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(label, field, value)

    try:
        db.commit()
        db.refresh(label)
        return label
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in updating record label: {str(error)}"
        )


def delete_record_label(db: Session, label_id: int) -> None:

    label = get_by_id(db, label_id)

    try:
        db.delete(label)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting record label: {str(error)}"
        )