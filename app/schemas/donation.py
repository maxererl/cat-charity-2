from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, PositiveInt


class DonationCreate(BaseModel):
    """Данные для создания пожертвования."""

    full_amount: PositiveInt
    comment: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class DonationDB(DonationCreate):
    """Пожертвование в ответе на его создание."""

    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    """Полная информация о пожертвовании и его распределении по проектам."""

    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None
