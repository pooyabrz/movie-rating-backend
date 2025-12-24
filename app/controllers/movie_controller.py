from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.schemas import MovieResponse, MovieCreate, RatingCreate, ResponseBase

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> MovieService:
    return MovieService(db)

@router.get("/", response_model=dict)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: MovieService = Depends(get_service)
):
    """List movies with pagination and aggregated ratings"""
    data = service.get_movies(page, page_size)
    return {"status": "success", "data": data}

@router.get("/{movie_id}", response_model=dict)
def get_movie(
    movie_id: int,
    service: MovieService = Depends(get_service)
):
    """Get detailed movie info"""
    data = service.get_movie_detail(movie_id)
    return {"status": "success", "data": data}

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie: MovieCreate,
    service: MovieService = Depends(get_service)
):
    """Create a new movie"""
    data = service.create_movie(movie)
    return {"status": "success", "data": data}

@router.delete("/{movie_id}", response_model=dict)
def delete_movie(
    movie_id: int,
    service: MovieService = Depends(get_service)
):
    """Delete a movie"""
    service.delete_movie(movie_id)
    return {"status": "success", "data": {"message": "Movie deleted"}}

@router.post("/{movie_id}/ratings", response_model=dict)
def rate_movie(
    movie_id: int,
    rating: RatingCreate,
    service: MovieService = Depends(get_service)
):
    """Rate a movie"""
    service.rate_movie(movie_id, rating.score)
    return {"status": "success", "data": {"message": "Rating added"}}