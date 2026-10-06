from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from schema.artist_schema import ArtistResponse
from schema.genre_schema import GenreResponse


class AlbumBase(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Title of the album",
        examples=["Best Album"]
    )

    release_year: int = Field(
        ...,
        ge=0,
        description="The year of the release",
        examples=[2010]
    )

    label_id: int = Field(
        ...,
        description="ID of the label",
        examples=[1]
    )


class AlbumCreate(AlbumBase):
    genre_ids: List[int] = Field(
            ...,
            min_length=1,
            description="IDs of the genres of the album",
            examples=[[1,2]]
    )
    artist_ids: List[int] = Field(
            ...,
            min_length=1,
            description="IDs of the artists of the album",
            examples=[[1,2]]
    )


class AlbumUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )

    release_year: Optional[int] = Field(
        None,
        ge=0
    )

    genre_ids: Optional[List[int]]=Field(None, min_length=1)

    artist_ids: Optional[List[int]]=Field(None, min_length=1)

    label_id: Optional[int] = None



class AlbumResponse(AlbumBase):
    id: int = Field(
        ...,
        description="Primary key of the album",
        examples=[1]
    )

    genres: List[GenreResponse]
    artists: List[ArtistResponse]
    cover_image_url: Optional[str] = Field(
        None,
        description="URL of the album cover",
        examples=["https://example.com/cover.jpg"]
    )

    model_config = ConfigDict(from_attributes=True)


class AlbumSummary(BaseModel):
    """
    Lightweight projection of an album without the genre and artist
    relations, used by the album list endpoint to avoid N+1 queries.
    """
    id: int = Field(
        ...,
        description="Primary key of the album",
        examples=[1]
    )
    title: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Kind of Blue"]
    )
    release_year: int = Field(
        ...,
        ge=0,
        examples=[1959]
    )
    label_id: int = Field(
        ...,
        examples=[1]
    )
    cover_image_url: Optional[str] = Field(
        None,
        examples=["https://example.com/cover.jpg"]
    )

    model_config = ConfigDict(from_attributes=True)
