from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.format_schema import (
    FormatCreate,
    FormatUpdate,
    FormatResponse
)
import controller.format_controller as controller


router = APIRouter(
    prefix="/formats",
    tags=["Formats"]
)


@router.get(
    "/",
    response_model=List[FormatResponse],
    status_code=status.HTTP_200_OK,
    summary="List all formats",
    description="Retrieve a paginated list of physical formats."
)
def read_formats(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db)
):
    return controller.get_all(db=db, skip=skip, limit=limit)


@router.get(
    "/{format_id}",
    response_model=FormatResponse,
    status_code=status.HTTP_200_OK,
    summary="Get format by ID",
    description="Retrieve detailed information for a specific physical format."
)
def read_format_by_id(
    format_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_by_id(db=db, format_id=format_id)


@router.post(
    "/",
    response_model=FormatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new format",
    description="Register a new physical format with name and optional description."
)
def create_new_format(
    format_data: FormatCreate,
    db: Session = Depends(get_db)
):
    return controller.create_format(db=db, format_data=format_data)


@router.put(
    "/{format_id}",
    response_model=FormatResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a format",
    description="Update an existing physical format by ID."
)
def update_format(
    format_id: int,
    format_data: FormatUpdate,
    db: Session = Depends(get_db)
):
    return controller.update_format(
        db=db, format_id=format_id, format_data=format_data
    )


@router.delete(
    "/{format_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a format",
    description="Remove a physical format from the database by ID."
)
def delete_format(
    format_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_format(db=db, format_id=format_id)
    return None