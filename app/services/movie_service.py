from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.movie_repository import MovieRepository
from app.schemas.schemas import MovieCreate, MovieResponse
from app.models.models import Director, Genre

class MovieService:
    """
    Business Logic Layer.
    Handles validation, calculations, and orchestration.
    """

    def __init__(self, db: Session):
        self.repo = MovieRepository(db)
        self.db = db # Needed only for validation checks (could be in another repo)

    def get_movies(self, page: int, page_size: int):
        skip = (page - 1) * page_size
        movies = self.repo.get_all(skip=skip, limit=page_size)
        
        # Append calculated stats
        results = []
        for movie in movies:
            stats = self.repo.get_rating_stats(movie.id)
            movie.average_rating = round(stats.average, 1) if stats.average else 0.0
            movie.ratings_count = stats.count
            results.append(movie)
        return results

    def get_movie_detail(self, movie_id: int):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        stats = self.repo.get_rating_stats(movie.id)
        movie.average_rating = round(stats.average, 1) if stats.average else 0.0
        movie.ratings_count = stats.count
        return movie

    def create_movie(self, movie_in: MovieCreate):
        # Validation: Check Director
        director = self.db.query(Director).filter(Director.id == movie_in.director_id).first()
        if not director:
             raise HTTPException(status_code=404, detail="Director not found")
        
        # Validation: Check Genres
        existing_genres = self.db.query(Genre).filter(Genre.id.in_(movie_in.genre_ids)).count()
        if existing_genres != len(movie_in.genre_ids):
             raise HTTPException(status_code=404, detail="One or more genres invalid")

        return self.repo.create(movie_in)

    def delete_movie(self, movie_id: int):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        self.repo.delete(movie)

    def rate_movie(self, movie_id: int, score: int):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
             raise HTTPException(status_code=404, detail="Movie not found")
        return self.repo.add_rating(movie_id, score)
