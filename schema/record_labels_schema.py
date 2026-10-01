from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RecordLabelBase(BaseModel):
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Name of the record label",
        examples=["Sub Pop"]
    )
    
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Country of origin",
        examples=["United States"]
    )
    
    website: Optional[str] = Field(
        None,
        max_length=255,
        description="Official website URL",
        examples=["https://www.subpop.com"]
    )


class RecordLabelCreate(RecordLabelBase):
    pass


class RecordLabelUpdate(BaseModel):
    
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    website: Optional[str] = Field(None, max_length=255)


class RecordLabelResponse(RecordLabelBase):
    
    id: int = Field(..., description="PK database", examples=[1])
    
    model_config = ConfigDict(from_attributes=True)