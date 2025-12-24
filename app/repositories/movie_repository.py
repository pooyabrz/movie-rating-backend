from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.models import Movie, MovieGenre, MovieRating, Director, Genre
from app.schemas.schemas import MovieCreate
from typing import List, Optional

class MovieRepository:
    """
    Data Access Layer for Movies.
    Strictly NO business logic here, only DB operations.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10) -> List[Movie]:
        """Fetch movies with pagination and relations"""
        return self.db.query(Movie).options(
            joinedload(Movie.director),
            joinedload(Movie.genres)
        ).offset(skip).limit(limit).all()

    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        return self.db.query(Movie).options(
            joinedload(Movie.director),
            joinedload(Movie.genres)
        ).filter(Movie.id == movie_id).first()

    def create(self, movie_data: MovieCreate) -> Movie:
        # Add Movie
        new_movie = Movie(
            title=movie_data.title,
            release_year=movie_data.release_year,
            cast=movie_data.cast,
            description=movie_data.description,
            director_id=movie_data.director_id
        )
        self.db.add(new_movie)
        self.db.commit()
        self.db.refresh(new_movie)

        # Add Genres (Many-to-Many)
        if movie_data.genre_ids:
            for genre_id in movie_data.genre_ids:
                stmt = movie_genres.insert().values(movie_id=new_movie.id, genre_id=genre_id)
                self.db.execute(stmt)
            self.db.commit()
        
        return self.get_by_id(new_movie.id)

    def delete(self, movie: Movie):
        self.db.delete(movie)
        self.db.commit()

    def add_rating(self, movie_id: int, score: int) -> MovieRating:
        rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def get_rating_stats(self, movie_id: int):
        """Calculates avg and count using SQL for performance"""
        return self.db.query(
            func.avg(MovieRating.score).label("average"),
            func.count(MovieRating.id).label("count")
        ).filter(MovieRating.movie_id == movie_id).first()
