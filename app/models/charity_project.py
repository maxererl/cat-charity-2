from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import InvestmentBase


class CharityProject(InvestmentBase):
    """Целевой проект благотворительного фонда.

    Attributes:
        name: Уникальное название проекта.
        description: Описание проекта.
    """

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)
