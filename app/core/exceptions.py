from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.common import error

# Handle error validation from Pydantic models. Return HTTP 422 (Unprocessable Entity).
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error(message="Validation error", data=jsonable_encoder(exc.errors())),
    )

# Handle error manual 'raise' return dinamic status code with template error message and data.
async def http_exception_handler(_request: Request, exc: HTTPException):
    msg = exc.detail if isinstance(exc.detail, str) else "Request error"
    return JSONResponse(
        status_code=exc.status_code,
        content=error(message=msg, data=None),
    )

# Handle error cause url notfound or method not allowed.
async def starlette_http_exception_handler(_request: Request, exc: StarletteHTTPException):
    msg = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(
        status_code=exc.status_code,
        content=error(message=msg, data=None),
    )

# Handle error cause python value error
async def value_error_handler(_request: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content=error(message=str(exc), data=None),
    )

# handle all error not handled before by app exception handler
async def unhandled_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(
        status_code=500,
        content=error(message="Internal server error", data=None),
    )

def include_app_exceptions(app):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
