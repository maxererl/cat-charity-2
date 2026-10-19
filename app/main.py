from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    openapi_tags=[
        {
            'name': 'charity_projects',
            'description': 'Целевые проекты фонда: сборы на конкретные цели.',
        },
        {
            'name': 'donations',
            'description': (
                'Пожертвования, которые автоматически распределяются '
                'по открытым проектам.'
            ),
        },
    ],
)

app.include_router(main_router)
