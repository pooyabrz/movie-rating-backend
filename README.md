# Movie Rating System Backend

## Overview

This is the backend API for the Movie Rating System (Phase 1). It provides a RESTful API for managing movies, directors, genres, and user ratings. Built with FastAPI, it offers high performance and automatic API documentation.

## Features

- **Movie Management**: Create, read, update, and list movies with filtering and pagination
- **Director and Genre Support**: Manage directors and genres with many-to-many relationships
- **User Ratings**: Add and view ratings for movies with aggregated statistics
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Automatic Migrations**: Database schema management with Alembic
- **Docker Support**: Easy deployment with Docker Compose
- **Comprehensive Logging**: Structured logging with configurable levels
- **Health Checks**: Built-in health endpoint for monitoring

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Async Support**: asyncpg for asynchronous database operations
- **Configuration**: Pydantic Settings with environment variables
- **Containerization**: Docker & Docker Compose
- **Testing**: (Add if applicable)

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized setup)
- PostgreSQL (if running locally without Docker)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd movie-rating-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix/Mac:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # Or if using poetry:
   poetry install
   ```

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/moviedb
PROJECT_NAME=Movie Rating System
API_V1_STR=/api/v1
LOG_LEVEL=INFO
SERVICE_NAME=movie-rating-api
```

## Running with Docker (Recommended)

1. Start the services:
   ```bash
   docker-compose up --build
   ```

2. The API will be available at `http://localhost:8000`
3. Database at `localhost:5432`

## Running Locally

1. Ensure PostgreSQL is running and create the database:
   ```sql
   CREATE DATABASE moviedb;
   ```

2. Run database migrations:
   ```bash
   alembic upgrade head
   ```

3. Seed the database (optional):
   ```bash
   # Run the seed script
   python scripts/seed_check.py
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database Migrations

- Create a new migration:
  ```bash
  alembic revision --autogenerate -m "Migration message"
  ```

- Apply migrations:
  ```bash
  alembic upgrade head
  ```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `GET /api/v1/movies` - List movies with pagination and filters
- `GET /api/v1/movies/{id}` - Get movie details
- `POST /api/v1/movies` - Create a new movie
- `PUT /api/v1/movies/{id}` - Update a movie
- `POST /api/v1/movies/{id}/ratings` - Add a rating
- `GET /health` - Health check

## Health Check

The application includes a health check endpoint at `/health` that returns `{"status": "ok"}`.

## Project Structure

```
movie-rating-backend/
├── app/
│   ├── controllers/     # API route handlers
│   ├── core/           # Configuration, logging, middleware
│   ├── db/             # Database session management
│   ├── exceptions/     # Error handlers
│   ├── models/         # SQLAlchemy models
│   ├── repositories/   # Data access layer
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── main.py         # FastAPI application
├── scripts/            # Utility scripts and seed data
├── alembic/            # Database migrations
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request