from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionDep
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
    project_id: Optional[int] = None,
) -> None:
    """Проверяет, что название проекта не занято другим проектом.

    Args:
        project_name: Проверяемое название.
        session: Асинхронная сессия базы данных.
        project_id: Идентификатор редактируемого проекта, который не должен
            считаться дубликатом самого себя.

    Raises:
        HTTPException: Если проект с таким названием уже существует (400).
    """
    project = await charity_project_crud.get_by_name(project_name, session)
    if project is not None and project.id != project_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def get_project_or_404(
    project_id: int, session: SessionDep
) -> CharityProject:
    """Возвращает проект по идентификатору из пути запроса.

    Args:
        project_id: Идентификатор проекта.
        session: Асинхронная сессия базы данных.

    Returns:
        Найденный проект.

    Raises:
        HTTPException: Если проекта с таким id не существует (404).
    """
    project = await charity_project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!',
        )
    return project


def check_project_is_open(project: CharityProject) -> None:
    """Проверяет, что проект ещё не закрыт.

    Args:
        project: Проверяемый проект.

    Raises:
        HTTPException: Если проект закрыт (400).
    """
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )


def check_full_amount_not_less_invested(
    project: CharityProject, full_amount: int
) -> None:
    """Проверяет, что новая требуемая сумма не меньше уже вложенной.

    Args:
        project: Редактируемый проект.
        full_amount: Новая требуемая сумма.

    Raises:
        HTTPException: Если сумма меньше вложенной (400).
    """
    if full_amount < project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=(
                'Нелья установить значение full_amount меньше уже '
                'вложенной суммы.'
            ),
        )


def check_project_has_no_investments(project: CharityProject) -> None:
    """Проверяет, что в проект ещё не вносили средства.

    Args:
        project: Проверяемый проект.

    Raises:
        HTTPException: Если в проект уже вложены средства (400).
    """
    if project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
