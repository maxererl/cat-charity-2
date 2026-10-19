from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, declared_attr, mapped_column
)

from app.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей.

    Имя таблицы формируется из имени класса в нижнем регистре.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет асинхронную сессию базы данных.

    Yields:
        AsyncSession: Сессия, которая закрывается после обработки запроса.
    """
    async with AsyncSessionLocal() as async_session:
        yield async_session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
