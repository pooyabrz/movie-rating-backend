from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, insert
from app.models.models import Movie, MovieRating, Director, Genre, movie_genres
from app.schemas.schemas import MovieCreate, MovieUpdate
from typing import List, Optional

class MovieRepository:
    """
    Data Access Layer for Movies.
    Strictly NO business logic here, only DB operations.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10, title: str = None, release_year: int = None, genre: str = None) -> List[Movie]:
        """Fetch movies with pagination, filtering and relations"""
        query = self.db.query(Movie).options(
            joinedload(Movie.director),
            joinedload(Movie.genres)
        )
        
        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if release_year:
            query = query.filter(Movie.release_year == release_year)
        if genre:
            query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))
        
        return query.offset(skip).limit(limit).all()


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
                # Use the table object for insert
                stmt = insert(movie_genres).values(movie_id=new_movie.id, genre_id=genre_id)
                self.db.execute(stmt)
            self.db.commit()
        
        # Refresh to load relationships
        return self.get_by_id(new_movie.id)

    def update(self, movie: Movie, movie_update: MovieUpdate) -> Movie:
        # Update basic fields
        update_data = movie_update.model_dump(exclude_unset=True)
        genre_ids = update_data.pop('genre_ids', None)
        
        for field, value in update_data.items():
            setattr(movie, field, value)
        
        # Update genres if provided
        if genre_ids is not None:
            # Remove existing genres
            self.db.execute(movie_genres.delete().where(movie_genres.c.movie_id == movie.id))
            # Add new genres
            if genre_ids:
                for genre_id in genre_ids:
                    stmt = insert(movie_genres).values(movie_id=movie.id, genre_id=genre_id)
                    self.db.execute(stmt)
        
        self.db.commit()
        self.db.refresh(movie)
        # Refresh to load relationships
        return self.get_by_id(movie.id)


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

    def get_ratings_for_movie(self, movie_id: int) -> List[MovieRating]:
        """Get all ratings for a specific movie"""
        return self.db.query(MovieRating).filter(MovieRating.movie_id == movie_id).order_by(MovieRating.rated_at.desc()).all()
