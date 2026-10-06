from fastapi import APIRouter, Depends, status, UploadFile,Query, File, Form
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
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db)
):
    return controller.get_all(db, skip, limit)
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
    title: str = Form(...),
    release_year: int = Form(...),
    genre_ids: List[int] = Form(...),
    artist_ids: List[int] = Form(...),
    label_id: int = Form(...),
    cover_image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    album_data = AlbumCreate(
        title=title,
        release_year=release_year,
        genre_ids=genre_ids,
        artist_ids=artist_ids,
        label_id=label_id
    )
    return controller.create_albums(
        db=db,
        album_data=album_data,
        cover_image=cover_image
    )


@router.put(
"/{album_id}",
    response_model=AlbumResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an album",
    description="Update existing album information by ID."
)
def update_album(
    album_id: int,
    title: str | None = Form(None),
    release_year: int | None = Form(None),
    genre_ids: List[int] | None = Form(None),
    artist_ids: List[int] | None = Form(None),
    label_id: int | None = Form(None),
    cover_image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    album_data = AlbumUpdate(
    title=title,
    release_year=release_year,
    genre_ids=genre_ids,
    artist_ids=artist_ids,
    label_id=label_id
    )
    return controller.update_album(
    db=db,
    album_id=album_id,
    album_data=album_data,
    cover_image=cover_image
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