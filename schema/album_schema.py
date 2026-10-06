from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

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

    genre_ids: List[int] = Field(
            ...,
            min_length=1,
            description="IDs of the genres of the album",
            examples=[[1, 2]]
    )

    artist_ids: List[int] = Field(
    ...,
    description="IDs of the artists",
    examples=[[1, 2]]
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

    label_id: Optional[int] = None

    artist_ids: Optional[List[int]] = None


class AlbumResponse(AlbumBase):
    id: int = Field(
        ...,
        description="Primary key of the album",
        examples=[1]
    )

    artist_ids: List[int] = Field(
    ...,
    description="IDs of the artists",
    examples=[[1, 2]]
    )

    cover_image_url: Optional[str] = Field(
        None,
        description="URL of the album cover",
        examples=["https://example.com/cover.jpg"]
    )

    model_config = ConfigDict(from_attributes=True)