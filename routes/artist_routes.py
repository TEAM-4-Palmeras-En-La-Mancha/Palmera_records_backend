from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.artist_schema import ArtistCreate, ArtistUpdate, ArtistResponse
import controller.artist_controller as controller


router = APIRouter(
    prefix="/artists",
    tags=["Artists"]
)


@router.get(
    "/",
    response_model=List[ArtistResponse],
    summary="Read all artists",
    description="Get all artists"
)
def read_artists(
    skip: int = Query(0, ge=0, description="Number record"),
    limit: int = Query(100, ge=1, le=100, description="Number record"),
    db: Session = Depends(get_db)
):
    return controller.get_all(db=db, skip=skip, limit=limit)


@router.get(
    "/{artist_id}",
    response_model=ArtistResponse,
    summary="Read an artist",
    description="Get an artist by id"
)
def read_artist(
    artist_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_by_id(db=db, artist_id=artist_id)


@router.post(
    "/",
    response_model=ArtistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new artist",
    description="Add an artist"
)
def create_new_artist(
    artist_data: ArtistCreate,
    db: Session = Depends(get_db)
):
    return controller.create_artist(db=db, artist_data=artist_data)


@router.put(
    "/{artist_id}",
    response_model=ArtistResponse,
    summary="Update an artist",
    description="Update an artist by id"
)
def update_existing_artist(
    artist_id: int,
    artist_data: ArtistUpdate,
    db: Session = Depends(get_db)
):
    return controller.update_artist(db=db, artist_id=artist_id, artist_data=artist_data)


@router.delete(
    "/{artist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an artist",
    description="Delete an artist, along with any album attributed solely to them."
)
def delete_existing_artist(
    artist_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_artist(db=db, artist_id=artist_id)
    return None