from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.logger import get_logger

logger = get_logger("app.exceptions")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, 'request_id', 'no-request-id')

    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
            "extra": {"detail": exc.detail}
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "failure",
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    request_id = getattr(request.state, 'request_id', 'no-request-id')

    # Extract validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        f"Validation error: {len(errors)} validation errors",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": 422,
            "extra": {"validation_errors": errors}
        }
    )

    return JSONResponse(
        status_code=422,
        content={
            "status": "failure",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors
            }
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors"""
    request_id = getattr(request.state, 'request_id', 'no-request-id')

    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "failure",
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Internal database error"
            }
        }
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    request_id = getattr(request.state, 'request_id', 'no-request-id')

    logger.critical(
        f"Unexpected error: {str(exc)}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "failure",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Unexpected error occurred"
            }
        }
    )