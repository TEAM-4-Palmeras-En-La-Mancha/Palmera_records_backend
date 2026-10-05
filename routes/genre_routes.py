from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.genre_schema import GenreCreate, GenreUpdate, GenreResponse
import controller.genre_controller as controller


router = APIRouter(
    prefix="/genres",
    tags=["Genres"]
)


@router.get(
    "/",
    response_model=List[GenreResponse],
    status_code=status.HTTP_200_OK,
    summary="Read all genres",
    description="Retrieve a paginated list of genres."
)
def read_genres(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db)
):
    return controller.get_all(db=db, skip=skip, limit=limit)


@router.get(
    "/{genre_id}",
    response_model=GenreResponse,
    status_code=status.HTTP_200_OK,
    summary="Get genre by ID",
    description="Retrieve detailed information for a specific genre."
)
def read_genre_by_id(
    genre_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_by_id(db=db, genre_id=genre_id)


@router.post(
    "/",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a genre",
    description="Register a new genre."
)
def create_new_genre(
    genre_data: GenreCreate,
    db: Session = Depends(get_db)
):
    return controller.create_genre(db=db, genre_data=genre_data)


@router.put(
    "/{genre_id}",
    response_model=GenreResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a genre",
    description="Update an existing genre by ID."
)
def update_existing_genre(
    genre_id: int,
    genre_data: GenreUpdate,
    db: Session = Depends(get_db)
):
    return controller.update_genre(
        db=db,
        genre_id=genre_id,
        genre_data=genre_data
    )


@router.delete(
    "/{genre_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a genre",
    description="Remove a genre. Albums are kept, only the association is removed."
)
def delete_existing_genre(
    genre_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_genre(db=db, genre_id=genre_id)
    return None