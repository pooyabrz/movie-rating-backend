import time
import uuid
from fastapi import Request, Response
from app.core.logger import get_logger

logger = get_logger("app.middleware")


async def request_logging_middleware(request: Request, call_next):
    """Middleware for logging HTTP requests and responses"""

    # Generate request ID
    request_id = str(uuid.uuid4())

    # Store request_id in request state for use in exception handlers
    request.state.request_id = request_id

    # Extract request info
    method = request.method
    path = request.url.path
    query_string = request.url.query
    if query_string:
        path = f"{path}?{query_string}"

    # Log request start
    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
        }
    )

    start_time = time.time()

    try:
        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log successful response
        log_level = "WARNING" if response.status_code >= 400 else "INFO"
        log_method = getattr(logger, log_level.lower())

        log_method(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )

        return response

    except Exception as e:
        # Calculate duration for failed requests
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log error response
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": 500,
                "duration_ms": duration_ms,
            },
            exc_info=True
        )
        raise