# Subtitle Translator API

A FastAPI-based service for downloading and translating video subtitles using AI. This service automatically downloads Hungarian subtitles from YouTube videos and translates them to multiple languages using OpenAI's translation capabilities.

## Features

- Download Hungarian subtitles from YouTube videos automatically
- Translate subtitles to multiple languages using OpenAI
- RESTful API with background task processing
- Automatic subtitle file management
- SQLite database with SQLAlchemy ORM (easily switchable to PostgreSQL)
- Interactive API documentation with Swagger UI

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- [OpenAI API key](https://platform.openai.com/api-keys) (for translations)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (installed automatically)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alitak/subtitle-translator-core.git
   cd subtitle-translator-core
   ```

2. Create and activate a virtual environment:
   ```bash
   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

### Configuration

Edit the `.env` file with your configuration:

```env
# Application
DEBUG=true
BASE_URL=http://localhost:8000

# Database (SQLite by default)
DATABASE_URL=sqlite:///./test.db

# OpenAI API Key (required for translations)
OPENAI_API_KEY=your_openai_api_key_here

# Storage directories (relative to project root)
STORAGE_DIR=storage
SUBTITLES_DIR=storage/subtitles
```

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## API Endpoints

### Videos

- `POST /api/v1/videos/` - Add a new video for processing
  - Request body: `{ "url": "youtube_url", "languages": ["en", "de"] }`
  - Automatically adds Hungarian as source language

- `GET /api/v1/videos/` - List all videos with pagination
  - Query params: `skip=0&limit=10`

- `GET /api/v1/videos/{video_id}` - Get video details

- `POST /api/v1/videos/{video_id}/subtitles/{language}` - Translate subtitles to a specific language
  - Language should be a 2-letter ISO code (e.g., 'en', 'de')

- `DELETE /api/v1/videos/{video_id}` - Delete a video and its subtitles

## Development

### Project Structure

```
app/
├── api/
│   └── v1/
│       └── endpoints/
│           └── videos.py      # API endpoints
├── core/
│   └── settings.py        # Application settings
├── db/
│   ├── base.py            # Database setup
│   └── models/              # SQLAlchemy models
├── schemas/                 # Pydantic models
├── services/                # Business logic
│   ├── video_service.py     # Video processing
│   └── translation_service.py # Translation logic
└── main.py                  # FastAPI application
```

### Database Migrations

This project uses Alembic for database migrations. To create and apply migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

Attila Kukel - [alitak@alitak.hu](mailto:alitak@alitak.hu)

Project Link: [https://github.com/alitak/subtitle-translator-core](https://github.com/alitak/subtitle-translator-core)

### 1. Add a new video
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/videos/' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://www.youtube.com/watch?v=example"
  }'
```

### 2. List all videos
```bash
curl 'http://localhost:8000/api/v1/videos/'
```

### 3. Translate subtitles
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/videos/{video_id}/subtitles' \
  -H 'Content-Type: application/json' \
  -d '{
    "language": "es"
  }'
```

## Configuration

The following environment variables can be configured in the `.env` file:

- `DATABASE_URL`: Database connection string (default: SQLite)
- `OPENAI_API_KEY`: Your OpenAI API key (required for translation)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: True)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
