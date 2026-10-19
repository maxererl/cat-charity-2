from fastapi import APIRouter

from app.core.db import SessionDep
from app.crud.donation import donation_crud
from app.schemas.donation import (
    DonationCreate, DonationDB, DonationFullInfoDB
)
from app.services.investment import invest_funds

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    description='Показать список всех пожертвований.',
)
async def get_all_donations(session: SessionDep):
    """Возвращает список всех пожертвований.

    Args:
        session: Асинхронная сессия базы данных.

    Returns:
        Список всех пожертвований с информацией об их распределении.
    """
    return await donation_crud.get_multi(session)


@router.post(
    '/',
    response_model=DonationDB,
    description='Создать пожертвование.',
)
async def create_donation(donation_in: DonationCreate, session: SessionDep):
    """Создаёт пожертвование и инвестирует его в открытые проекты.

    Создание пожертвования и инвестирование выполняются в одной транзакции.

    Args:
        donation_in: Данные нового пожертвования.
        session: Асинхронная сессия базы данных.

    Returns:
        Созданное пожертвование.
    """
    new_donation = await donation_crud.create(
        donation_in, session, commit=False
    )
    return await invest_funds(new_donation, session)
