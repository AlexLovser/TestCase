"""
Модуль аутентификации по API ключу
"""
import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
correct_api_key = os.getenv("API_KEY")


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Проверка API ключа из заголовка запроса

    Args:
        api_key: API ключ из заголовка X-API-Key

    Returns:
        str: Валидный API ключ

    Raises:
        HTTPException: Если ключ неверный или отсутствует
    """

    if api_key != correct_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный API ключ"
        )

    return api_key

