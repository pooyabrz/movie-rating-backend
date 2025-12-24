from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from datetime import datetime
from app.models.base import Base

# Association Table for Many-to-Many (Movies <-> Genres)
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

class Director(Base):
    """Director Model"""
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    birth_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    movies: Mapped[List["Movie"]] = relationship(back_populates="director")

class Genre(Base):
    """Genre Model"""
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    movies: Mapped[List["Movie"]] = relationship(secondary=movie_genres, back_populates="genres")

class Movie(Base):
    """Movie Model"""
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    release_year: Mapped[int] = mapped_column(Integer)
    cast: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    director_id: Mapped[int] = mapped_column(Integer, ForeignKey("directors.id"))

    # Relationships
    director: Mapped["Director"] = relationship(back_populates="movies")
    genres: Mapped[List["Genre"]] = relationship(secondary=movie_genres, back_populates="movies")
    ratings: Mapped[List["MovieRating"]] = relationship(back_populates="movie", cascade="all, delete-orphan")

class MovieRating(Base):
    """Movie Rating Model"""
    __tablename__ = "movie_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    score: Mapped[int] = mapped_column(Integer) # Validator needed in App layer for 1-10
    rated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))

    # Relationship
    movie: Mapped["Movie"] = relationship(back_populates="ratings")
