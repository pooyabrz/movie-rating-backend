from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.schemas import MovieResponse, MovieCreate, MovieUpdate, RatingCreate, RatingResponse, ResponseBase

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> MovieService:
    return MovieService(db)

@router.get("/", response_model=dict)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    title: str = Query(None),
    release_year: int = Query(None),
    genre: str = Query(None),
    service: MovieService = Depends(get_service)
):
    """List movies with pagination, filtering and aggregated ratings"""
    data = service.get_movies(page, page_size, title=title, release_year=release_year, genre=genre)

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

@router.put("/{movie_id}", response_model=dict)
def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    service: MovieService = Depends(get_service)
):
    """Update a movie"""
    data = service.update_movie(movie_id, movie_update)
    return {"status": "success", "data": data}

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    service: MovieService = Depends(get_service)
):
    """Delete a movie"""
    service.delete_movie(movie_id)
    return

@router.post("/{movie_id}/ratings", response_model=dict, status_code=status.HTTP_201_CREATED)
def rate_movie(
    movie_id: int,
    score: int = Query(..., ge=1, le=10),
    service: MovieService = Depends(get_service)
):
    """Rate a movie"""
    service.rate_movie(movie_id, score)
    return {"status": "success", "data": {"message": "Rating added"}}

@router.get("/{movie_id}/ratings", response_model=dict)
def get_movie_ratings(
    movie_id: int,
    service: MovieService = Depends(get_service)
):
    """Get all ratings for a movie"""
    data = service.get_movie_ratings(movie_id)
    return {"status": "success", "data": data}