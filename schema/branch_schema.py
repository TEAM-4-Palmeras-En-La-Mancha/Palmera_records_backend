
from pydantic import BaseModel, ConfigDict, Field

class BranchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=1, max_length=20)

# ---POST (create) ---
class BranchCreate(BranchBase):
    pass

# --- UPDATE (PUT/PATCH) ---
class BranchUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = Field(None, min_length=1, max_length=200)
    phone: str | None = Field(None, min_length=1, max_length=20)

# --- READ (GET) ---
class BranchRead(BranchBase):
    id: int

    model_config = ConfigDict(from_attributes=True)