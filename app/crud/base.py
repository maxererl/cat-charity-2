from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import InvestmentBase

ModelType = TypeVar('ModelType', bound=InvestmentBase)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType]):
    """Базовый класс с операциями чтения и создания для ORM-модели.

    Attributes:
        model: ORM-модель, с которой работает объект.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self, obj_id: int, session: AsyncSession
    ) -> Optional[ModelType]:
        """Возвращает объект по идентификатору.

        Args:
            obj_id: Идентификатор объекта.
            session: Асинхронная сессия базы данных.

        Returns:
            Найденный объект или None, если объекта с таким id нет.
        """
        return await session.get(self.model, obj_id)

    async def get_multi(self, session: AsyncSession) -> list[ModelType]:
        """Возвращает все объекты модели.

        Args:
            session: Асинхронная сессия базы данных.

        Returns:
            Список всех объектов.
        """
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def get_open_ordered(self, session: AsyncSession) -> list[ModelType]:
        """Возвращает не полностью инвестированные объекты от старых к новым.

        Args:
            session: Асинхронная сессия базы данных.

        Returns:
            Список объектов с `fully_invested=False`, отсортированный
            по дате создания.
        """
        db_objs = await session.execute(
            select(self.model)
            .where(self.model.fully_invested.is_(False))
            .order_by(self.model.create_date, self.model.id)
        )
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        commit: bool = True,
    ) -> ModelType:
        """Создаёт объект по данным схемы.

        Args:
            obj_in: Схема с данными нового объекта.
            session: Асинхронная сессия базы данных.
            commit: Если True, транзакция фиксируется и объект обновляется
                из базы. Если False, изменения только передаются в базу
                в рамках открытой транзакции, а фиксация остаётся на вызывающем
                коде.

        Returns:
            Созданный объект.
        """
        db_obj = self.model(**obj_in.model_dump())
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        else:
            await session.flush()
        return db_obj
