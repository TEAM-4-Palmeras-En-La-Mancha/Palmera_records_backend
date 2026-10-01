from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FormatBase(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Name of the physical format",
        examples=["Vinyl"]
    )

    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Short description of the format",
        examples=["LP 12 inches, 33 rpm"]
    )


class FormatCreate(FormatBase):
    pass


class FormatUpdate(BaseModel):

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class FormatResponse(FormatBase):

    id: int = Field(..., description="PK database", examples=[1])

    model_config = ConfigDict(from_attributes=True)