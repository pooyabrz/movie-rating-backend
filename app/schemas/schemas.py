from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

# --- Response Standard ---
class ResponseBase(BaseModel):
    status: str
    data: Optional[dict | list] = None
    error: Optional[str] = None

# --- Models ---

class GenreResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class DirectorResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class MovieBase(BaseModel):
    title: str = Field(..., min_length=1)
    release_year: int = Field(..., gt=1880)
    cast: Optional[str] = None
    description: Optional[str] = None

class MovieCreate(MovieBase):
    director_id: int
    genre_ids: List[int]

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    release_year: Optional[int] = Field(None, gt=1880)
    cast: Optional[str] = None
    description: Optional[str] = None
    director_id: Optional[int] = None
    genre_ids: Optional[List[int]] = None

class MovieResponse(MovieBase):
    id: int
    director: DirectorResponse
    genres: List[GenreResponse]
    average_rating: Optional[float] = 0.0
    ratings_count: Optional[int] = 0

    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)

class RatingResponse(BaseModel):
    id: int
    score: int
    rated_at: datetime
    class Config:
        from_attributes = True
