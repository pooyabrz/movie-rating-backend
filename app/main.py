from fastapi import FastAPI
from app.core.config import settings
from app.controllers import movie_controller

app = FastAPI(title=settings.PROJECT_NAME)

# Include Routers
app.include_router(movie_controller.router, prefix=f"{settings.API_V1_STR}/movies", tags=["Movies"])

@app.get("/health")
def health_check():
    return {"status": "ok"}