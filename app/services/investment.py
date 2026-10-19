from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import CharityProject
from app.models.base import InvestmentBase


async def invest_funds(
    new_obj: InvestmentBase, session: AsyncSession
) -> InvestmentBase:
    """Распределяет средства между новым объектом и открытыми объектами.

    Для нового проекта источниками средств служат нераспределённые
    пожертвования, для нового пожертвования - открытые проекты. Средства
    распределяются от самых старых источников к самым новым. Все изменения
    фиксируются одним вызовом `session.commit()` в конце функции.

    Args:
        new_obj: Только что созданный проект или пожертвование, добавленный
            в сессию, но ещё не зафиксированный в базе.
        session: Асинхронная сессия базы данных.

    Returns:
        Новый объект с учётом выполненных инвестиций.
    """
    if isinstance(new_obj, CharityProject):
        sources = await donation_crud.get_open_ordered(session)
    else:
        sources = await charity_project_crud.get_open_ordered(session)

    close_date = datetime.now()
    for source in sources:
        amount = min(
            new_obj.full_amount - new_obj.invested_amount,
            source.full_amount - source.invested_amount,
        )
        new_obj.invested_amount += amount
        source.invested_amount += amount
        new_obj.close_if_fully_invested(close_date)
        source.close_if_fully_invested(close_date)
        if new_obj.fully_invested:
            break

    await session.commit()
    await session.refresh(new_obj)
    return new_obj
