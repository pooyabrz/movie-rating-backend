from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.movie_repository import MovieRepository
from app.schemas.schemas import MovieCreate, MovieResponse, MovieUpdate, RatingResponse
from app.models.models import Director, Genre
from app.core.logger import get_logger

logger = get_logger("app.services")

class MovieService:
    """
    Business Logic Layer.
    Handles validation, calculations, and orchestration.
    """

    def __init__(self, db: Session):
        self.repo = MovieRepository(db)
        self.db = db # Needed only for validation checks (could be in another repo)

    def get_movies(self, page: int, page_size: int, title: str = None, release_year: int = None, genre: str = None):
        skip = (page - 1) * page_size
        movies = self.repo.get_all(skip=skip, limit=page_size, title=title, release_year=release_year, genre=genre)

        
        # Append calculated stats
        results = []
        for movie in movies:
            stats = self.repo.get_rating_stats(movie.id)
            movie_response = MovieResponse.from_orm(movie)
            movie_response.average_rating = round(stats.average, 1) if stats.average else 0.0
            movie_response.ratings_count = stats.count
            results.append(movie_response)

        return results

    def get_movie_detail(self, movie_id: int):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        stats = self.repo.get_rating_stats(movie.id)
        movie_response = MovieResponse.from_orm(movie)
        movie_response.average_rating = round(stats.average, 1) if stats.average else 0.0
        movie_response.ratings_count = stats.count
        return movie_response


    def create_movie(self, movie_in: MovieCreate):
        # Validation: Check Director
        director = self.db.query(Director).filter(Director.id == movie_in.director_id).first()
        if not director:
            logger.warning(f"Director not found: {movie_in.director_id}")
            raise HTTPException(status_code=404, detail="Director not found")
        
        # Validation: Check Genres
        existing_genres = self.db.query(Genre).filter(Genre.id.in_(movie_in.genre_ids)).count()
        if existing_genres != len(movie_in.genre_ids):
            logger.warning(f"One or more genres invalid: {movie_in.genre_ids}")
            raise HTTPException(status_code=404, detail="One or more genres invalid")

        movie = self.repo.create(movie_in)
        logger.info(f"Movie created: {movie.id} - {movie.title}")
        movie_response = MovieResponse.from_orm(movie)
        movie_response.average_rating = 0.0
        movie_response.ratings_count = 0
        return movie_response

    def update_movie(self, movie_id: int, movie_update: MovieUpdate):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
            logger.warning(f"Movie not found for update: {movie_id}")
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Validation: Check Director if provided
        if movie_update.director_id:
            director = self.db.query(Director).filter(Director.id == movie_update.director_id).first()
            if not director:
                logger.warning(f"Director not found for update: {movie_update.director_id}")
                raise HTTPException(status_code=404, detail="Director not found")
        
        # Validation: Check Genres if provided
        if movie_update.genre_ids:
            existing_genres = self.db.query(Genre).filter(Genre.id.in_(movie_update.genre_ids)).count()
            if existing_genres != len(movie_update.genre_ids):
                logger.warning(f"One or more genres invalid for update: {movie_update.genre_ids}")
                raise HTTPException(status_code=404, detail="One or more genres invalid")

        updated_movie = self.repo.update(movie, movie_update)
        logger.info(f"Movie updated: {movie_id} - {updated_movie.title}")
        stats = self.repo.get_rating_stats(updated_movie.id)
        movie_response = MovieResponse.from_orm(updated_movie)
        movie_response.average_rating = round(stats.average, 1) if stats.average else 0.0
        movie_response.ratings_count = stats.count
        return movie_response


    def delete_movie(self, movie_id: int):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
            logger.warning(f"Movie not found for deletion: {movie_id}")
            raise HTTPException(status_code=404, detail="Movie not found")
        logger.warning(f"Movie deleted: {movie_id} - {movie.title}")
        self.repo.delete(movie)

    def rate_movie(self, movie_id: int, score: int):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
            logger.warning(f"Movie not found for rating: {movie_id}")
            raise HTTPException(status_code=404, detail="Movie not found")
        rating = self.repo.add_rating(movie_id, score)
        logger.info(f"Rating added: movie_id={movie_id}, score={score}, rating_id={rating.id}")
        return rating

    def get_movie_ratings(self, movie_id: int):
        movie = self.repo.get_by_id(movie_id)
        if not movie:
            logger.warning(f"Movie not found for ratings retrieval: {movie_id}")
            raise HTTPException(status_code=404, detail="Movie not found")
        
        ratings = self.repo.get_ratings_for_movie(movie_id)
        logger.info(f"Retrieved {len(ratings)} ratings for movie: {movie_id}")
        return [RatingResponse.from_orm(rating) for rating in ratings]
