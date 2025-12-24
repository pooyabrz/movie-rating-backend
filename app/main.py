from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.logger import setup_logging, get_logger
from app.core.middleware import request_logging_middleware
from app.exceptions.handlers import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    global_exception_handler
)
from app.controllers import movie_controller

# Setup logging first
setup_logging()
logger = get_logger("app.main")

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# Add request logging middleware
app.middleware("http")(request_logging_middleware)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include Routers
app.include_router(movie_controller.router, prefix=f"{settings.API_V1_STR}/movies", tags=["Movies"])

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}
