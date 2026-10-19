from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Описание ошибки в ответе API."""

    detail: str
