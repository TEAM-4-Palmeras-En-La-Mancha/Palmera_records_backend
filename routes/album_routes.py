from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from controller import album_controller as controller

from core.database import get_db
from schema.album_schema import AlbumCreate,AlbumUpdate,AlbumResponse

router = APIRouter(
    prefix= "/albums",
    tags=["Albums"]
)

@router.get(
    "/",
        response_model=List[AlbumResponse],
    status_code=status.HTTP_200_OK,
    summary="List all albums",
    description="Retrieve a paginated list of albums."
)
def get_albums(
    db:Session = Depends(get_db)
):
    return controller.get_all(db)
@router.get(
"/{album_id}",
    response_model=AlbumResponse,
    status_code=status.HTTP_200_OK,
    summary="Get album by ID",
    description="Retrieve detailed information for a specific album."
)
def read_album_by_id(
album_id: int,
db: Session = Depends(get_db)
):
    return controller.get_by_id(db=db, album_id=album_id)
@router.post(
    "/",
    response_model=AlbumResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a album"
)
def post_album(
    album_data: AlbumCreate,
    db: Session = Depends(get_db)
):
    return controller.create_albums(db, album_data)
@router.put(
"/{album_id}",
    response_model=AlbumResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an album",
    description="Update existing album information by ID."
)
def update_album(
    album_id: int,
    album_data: AlbumUpdate,
    db: Session = Depends(get_db)
):
    return controller.update_album(
        db=db,
        album_id=album_id,
        album_data=album_data
    )

@router.delete(
"/{album_id}",
status_code=status.HTTP_204_NO_CONTENT,
summary="Delete an album",
description="Remove an album from the database by ID."
)
def delete_album(
    album_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_Album(db=db, album_id=album_id)
    return None