from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.validators import (
    check_full_amount_not_less_invested, check_name_duplicate,
    check_project_has_no_investments, check_project_is_open,
    get_project_or_404
)
from app.core.db import SessionDep
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.schemas.error import ErrorDetail
from app.services.investment import invest_funds

router = APIRouter()

ProjectDep = Annotated[CharityProject, Depends(get_project_or_404)]


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    description='Показать список всех целевых проектов.',
)
async def get_all_charity_projects(session: SessionDep):
    """Возвращает список всех целевых проектов.

    Args:
        session: Асинхронная сессия базы данных.

    Returns:
        Список всех проектов.
    """
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    responses={
        HTTPStatus.BAD_REQUEST: {
            'model': ErrorDetail,
            'description': 'Проект с таким именем уже существует.',
        },
    },
    description='Создать целевой проект.',
)
async def create_charity_project(
    project_in: CharityProjectCreate, session: SessionDep
):
    """Создаёт целевой проект и инвестирует в него свободные пожертвования.

    Создание проекта и инвестирование выполняются в одной транзакции.

    Args:
        project_in: Данные нового проекта.
        session: Асинхронная сессия базы данных.

    Returns:
        Созданный проект с учётом выполненных инвестиций.

    Raises:
        HTTPException: Если проект с таким названием уже существует (400).
    """
    await check_name_duplicate(project_in.name, session)
    new_project = await charity_project_crud.create(
        project_in, session, commit=False
    )
    return await invest_funds(new_project, session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    responses={
        HTTPStatus.BAD_REQUEST: {
            'model': ErrorDetail,
            'description': 'Недопустимое редактирование проекта.',
        },
        HTTPStatus.NOT_FOUND: {
            'model': ErrorDetail,
            'description': 'Проект не существует.',
        },
    },
    description=(
        'Редактировать целевой проект.\n\n'
        'Закрытый проект нельзя редактировать;\n'
        'нельзя установить требуемую сумму меньше уже вложенной.'
    ),
)
async def update_charity_project(
    project_in: CharityProjectUpdate,
    project: ProjectDep,
    session: SessionDep,
):
    """Редактирует целевой проект.

    Args:
        project_in: Новые значения полей проекта.
        project: Редактируемый проект, найденный по id из пути запроса.
        session: Асинхронная сессия базы данных.

    Returns:
        Обновлённый проект.

    Raises:
        HTTPException: Если проект закрыт, название занято или требуемая
            сумма меньше уже вложенной (400).
    """
    check_project_is_open(project)
    if project_in.name is not None:
        await check_name_duplicate(project_in.name, session, project.id)
    if project_in.full_amount is not None:
        check_full_amount_not_less_invested(project, project_in.full_amount)
    return await charity_project_crud.update(project, project_in, session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    responses={
        HTTPStatus.BAD_REQUEST: {
            'model': ErrorDetail,
            'description': 'В проект уже были внесены средства.',
        },
        HTTPStatus.NOT_FOUND: {
            'model': ErrorDetail,
            'description': 'Проект не существует.',
        },
    },
    description=(
        'Удалить целевой проект.\n\n'
        'Нельзя удалить проект, в который уже были инвестированы средства.'
    ),
)
async def delete_charity_project(project: ProjectDep, session: SessionDep):
    """Удаляет целевой проект, в который ещё не вносились средства.

    Args:
        project: Удаляемый проект, найденный по id из пути запроса.
        session: Асинхронная сессия базы данных.

    Returns:
        Удалённый проект.

    Raises:
        HTTPException: Если в проект уже были внесены средства (400).
    """
    check_project_has_no_investments(project)
    return await charity_project_crud.remove(project, session)
