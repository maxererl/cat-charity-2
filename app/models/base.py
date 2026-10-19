from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class InvestmentBase(Base):
    """Абстрактная модель с общими полями проекта и пожертвования.

    Таблица для этого класса в базе данных не создаётся.

    Attributes:
        full_amount: Полная сумма (требуемая для проекта или внесённая).
        invested_amount: Сумма, которая уже распределена.
        fully_invested: Признак того, что полная сумма распределена.
        create_date: Дата и время создания записи.
        close_date: Дата и время, когда полная сумма была распределена.
    """

    __abstract__ = True

    full_amount: Mapped[int]
    invested_amount: Mapped[int] = mapped_column(default=0)
    fully_invested: Mapped[bool] = mapped_column(default=False)
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    def close_if_fully_invested(self, close_date: datetime) -> None:
        """Закрывает запись, если полная сумма уже распределена.

        Args:
            close_date: Дата и время закрытия, которые будут записаны
                в поле `close_date`.
        """
        if self.invested_amount >= self.full_amount:
            self.fully_invested = True
            self.close_date = close_date
