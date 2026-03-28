from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    status: bool
    message: str
    data: Any | None = None


def success(message: str = "Success", data: Any | None = None) -> dict:
    return ApiResponse(
        status=True,
        message=message,
        data=data,
    ).model_dump()


def info(message: str = "Ok") -> dict:
    return ApiResponse(
        status=True,
        message=message,
    ).model_dump()


def error(message: str = "Error", data : Any | None = None) -> dict:
    return ApiResponse(
        status=False,
        message=message,
        data=data,
    ).model_dump()
