from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GenreBase(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="Genre name",
        examples=["Jazz"]
    )


class GenreCreate(GenreBase):
    pass


class GenreUpdate(BaseModel):

    name: Optional[str] = Field(None, min_length=1, max_length=80)


class GenreResponse(GenreBase):

    id: int = Field(..., description="PK database", examples=[1])

    model_config = ConfigDict(from_attributes=True)