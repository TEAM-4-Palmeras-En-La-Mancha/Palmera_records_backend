from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.album_format_schema import (
    AlbumFormatCreate,
    AlbumFormatUpdate,
    AlbumFormatResponse
)
import controller.album_format_controller as controller


router = APIRouter(
    prefix="/album-formats",
    tags=["Album Formats"]
)


@router.get(
    "/",
    response_model=List[AlbumFormatResponse],
    status_code=status.HTTP_200_OK,
    summary="List all album formats",
    description="Retrieve a paginated list of album editions with price and stock."
)
def read_album_formats(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db)
):
    return controller.get_all(db=db, skip=skip, limit=limit)


@router.get(
    "/{album_id}/{format_id}",
    response_model=AlbumFormatResponse,
    status_code=status.HTTP_200_OK,
    summary="Get an album format",
    description="Retrieve a specific edition of an album in a specific physical format."
)
def read_album_format_by_id(
    album_id: int,
    format_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_by_id(
        db=db, album_id=album_id, format_id=format_id
    )


@router.post(
    "/",
    response_model=AlbumFormatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new album format",
    description="Register a new edition of an album in a physical format, with its price and stock."
)
def create_new_album_format(
    album_format_data: AlbumFormatCreate,
    db: Session = Depends(get_db)
):
    return controller.create_album_format(
        db=db, album_format_data=album_format_data
    )


@router.put(
    "/{album_id}/{format_id}",
    response_model=AlbumFormatResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an album format",
    description="Update price or stock of an existing edition."
)
def update_album_format(
    album_id: int,
    format_id: int,
    album_format_data: AlbumFormatUpdate,
    db: Session = Depends(get_db)
):
    return controller.update_album_format(
        db=db,
        album_id=album_id,
        format_id=format_id,
        album_format_data=album_format_data
    )


@router.delete(
    "/{album_id}/{format_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an album format",
    description="Remove a specific edition of an album in a physical format."
)
def delete_album_format(
    album_id: int,
    format_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_album_format(
        db=db, album_id=album_id, format_id=format_id
    )
    return None