from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AlbumFormatBase(BaseModel):

    album_id: int = Field(
        ...,
        gt=0,
        description="ID of the album",
        examples=[1]
    )

    format_id: int = Field(
        ...,
        gt=0,
        description="ID of the physical format",
        examples=[1]
    )

    price: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Price of this edition",
        examples=["24.90"]
    )

    stock: int = Field(
        0,
        ge=0,
        description="Units available",
        examples=[50]
    )


class AlbumFormatCreate(AlbumFormatBase):
    pass


class AlbumFormatUpdate(BaseModel):

    price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)


class AlbumFormatResponse(AlbumFormatBase):

    model_config = ConfigDict(from_attributes=True)