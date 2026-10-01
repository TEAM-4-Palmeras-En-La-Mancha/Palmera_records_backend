from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from enums.genres_enum import Genres

class AlbumBase(BaseModel):
       title: str = Field(
           ...,         
            min_length=2,
            max_length=100,
            description="Title of the album",
            examples=["Best Album"]
       )

       artist: str = Field(
              ...,
              min_length=2,
            max_length=100,
            description="Name of the artist",
            examples=["Best Singer"]
        )
       release_year: int = Field(
              ...,
              ge=0,
              description="The year of the release",
              examples=[2010]
       )
       genre: Genres =Field(
              ...,
              description="Genre of the album",
              examples=["jazz"]
       )
       cover_image_url: Optional[str] = Field(
        None,
        description="URL of the album cover",
        examples=["https://example.com/cover.jpg"]
    )
       label_id: int = Field(
        ...,
        description="ID of the label",
        examples=[1]
    )

class AlbumCreate(AlbumBase):
       pass
class AnimalUpdate(BaseModel):
    title: Optional[str] = Field(
        None,         
        min_length=2,
        max_length=100,
    )
    artist: Optional[str] = Field(
        None,         
        min_length=2,
        max_length=100,
    )

    release_year:Optional[int]= Field(
        None,
        ge=0
    )
    genre:Optional[Genres]=None

    cover_image_url:Optional[str]= Field(
          None,
        min_length=2,
        max_length=100
    )
    label_id: Optional[int]= None

class AlbumResponse(AlbumBase):
      id:int = Field(
            ...,
            description="PRimary key of the album",
            examples=[1]
      )

      model_config = ConfigDict(from_attributes=True)
