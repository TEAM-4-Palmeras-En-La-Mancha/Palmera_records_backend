from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.record_labels_schema import (
    RecordLabelCreate,
    RecordLabelUpdate,
    RecordLabelResponse
)
import controller.record_labels_controller as controller


router = APIRouter(
    prefix="/record-labels",
    tags=["Record Labels"]
)


@router.get(
    "/",
    response_model=List[RecordLabelResponse],
    status_code=status.HTTP_200_OK,
    summary="List all record labels",
    description="Retrieve a paginated list of record labels."
)
def read_record_labels(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db)
):
    return controller.get_all(db=db, skip=skip, limit=limit)


@router.get(
    "/{label_id}",
    response_model=RecordLabelResponse,
    status_code=status.HTTP_200_OK,
    summary="Get record label by ID",
    description="Retrieve detailed information for a specific record label."
)
def read_record_label_by_id(
    label_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_by_id(db=db, label_id=label_id)


@router.post(
    "/",
    response_model=RecordLabelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new record label",
    description="Register a new record label with name, country, and optional website."
)
def create_new_record_label(
    label_data: RecordLabelCreate,
    db: Session = Depends(get_db)
):
    return controller.create_record_label(db=db, label_data=label_data)


@router.put(
    "/{label_id}",
    response_model=RecordLabelResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a record label",
    description="Update existing record label information by ID."
)
def update_record_label(
    label_id: int,
    label_data: RecordLabelUpdate,
    db: Session = Depends(get_db)
):
    return controller.update_record_label(db=db, label_id=label_id, label_data=label_data)


@router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a record label",
    description="Remove a record label from the database by ID."
)
def delete_record_label(
    label_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_record_label(db=db, label_id=label_id)
    return None