from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class CharityProjectCreate(BaseModel):
    """Данные для создания целевого проекта."""

    name: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10)
    full_amount: PositiveInt

    model_config = ConfigDict(extra='forbid')


class CharityProjectUpdate(BaseModel):
    """Данные для редактирования целевого проекта."""

    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[PositiveInt] = None

    model_config = ConfigDict(extra='forbid')


class CharityProjectDB(CharityProjectCreate):
    """Целевой проект в ответах API."""

    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
