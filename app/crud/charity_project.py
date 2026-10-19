from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate
)


class CRUDCharityProject(CRUDBase[CharityProject, CharityProjectCreate]):
    """Операции с целевыми проектами."""

    async def get_by_name(
        self, name: str, session: AsyncSession
    ) -> Optional[CharityProject]:
        """Возвращает проект по его названию.

        Args:
            name: Название проекта.
            session: Асинхронная сессия базы данных.

        Returns:
            Найденный проект или None, если проекта с таким названием нет.
        """
        db_project = await session.execute(
            select(CharityProject).where(CharityProject.name == name)
        )
        return db_project.scalars().first()

    async def update(
        self,
        db_project: CharityProject,
        project_in: CharityProjectUpdate,
        session: AsyncSession,
    ) -> CharityProject:
        """Обновляет проект переданными полями.

        Если после обновления требуемая сумма равна внесённой, проект
        закрывается.

        Args:
            db_project: Редактируемый проект.
            project_in: Схема с новыми значениями полей.
            session: Асинхронная сессия базы данных.

        Returns:
            Обновлённый проект.
        """
        for field, value in project_in.model_dump(exclude_none=True).items():
            setattr(db_project, field, value)
        db_project.close_if_fully_invested(datetime.now())
        session.add(db_project)
        await session.commit()
        await session.refresh(db_project)
        return db_project

    async def remove(
        self, db_project: CharityProject, session: AsyncSession
    ) -> CharityProject:
        """Удаляет проект.

        Args:
            db_project: Удаляемый проект.
            session: Асинхронная сессия базы данных.

        Returns:
            Удалённый проект.
        """
        await session.delete(db_project)
        await session.commit()
        return db_project


charity_project_crud = CRUDCharityProject(CharityProject)
