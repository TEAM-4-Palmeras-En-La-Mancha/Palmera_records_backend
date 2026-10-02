from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ArtistBase(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Artist name",
        examples=["Vetusta Morla"]
    )

    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="Artist biography",
        examples=["Spanish indie rock band formed in 1998."]
    )

class ArtistCreate(ArtistBase):
    pass

class ArtistUpdate(BaseModel):

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    bio: Optional[str] = Field(None, max_length=500)

class ArtistResponse(ArtistBase):

    id: int = Field(..., description="PK database", examples=[1])

    model_config = ConfigDict(from_attributes=True)

    