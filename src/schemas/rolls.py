from datetime import date

from pydantic import BaseModel, Field


class RollsCreate(BaseModel):
    length: int = Field(..., gt=0)
    weight: int = Field(..., gt=0)


class Rolls(RollsCreate):
    id: int = Field(..., gt=0)
    is_deleted: bool
    create_at: date
    delete_at: date | None
