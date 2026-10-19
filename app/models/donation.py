from typing import Optional

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import InvestmentBase


class Donation(InvestmentBase):
    """Пожертвование в благотворительный фонд.

    Attributes:
        comment: Необязательный комментарий к пожертвованию.
    """

    comment: Mapped[Optional[str]] = mapped_column(Text)
