# HH Parser

HH Parser is an automated job application tool for the HeadHunter (hh.ru) platform. It uses browser automation to search for jobs and submit applications based on specified criteria.

## Prerequisites

- Docker and Docker Compose
- Git

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd HHParser
   ```

2. Ensure Docker and Docker Compose are installed and running.

## Configuration

1. Copy or create the environment file:

   ```bash
   cp .env.test .env
   ```

2. Edit `.env` file with your configuration:
   - Set Redis connection details if needed
   - Configure any environment-specific variables

3. Review and modify `.env` file for environment settings:
   - APP_ENVIRONMENT: Application environment (dev/prod)
   - LOG_LEVEL: Logging level
   - DEBUG: Debug mode flag
   - REDIS_URL: Redis connection URL
   - CELERY_BROKER_URL: Celery broker URL
   - CELERY_RESULT_BACKEND: Celery result backend URL
   - CORS_ALLOW_ORIGINS: Allowed CORS origins

   Application settings (selectors, timeouts, etc.) are configured in the code with default values and can be overridden via environment variables if needed.

## Running the Application

1. Build and start the services:

   ```bash
   docker-compose up --build
   ```

   This will start:
   - Redis (database and message queue)
   - Web service (FastAPI application with frontend)
   - Worker service (Celery for background job processing)

2. Access the web interface at `http://localhost:8000`

## Usage

1. Open the web interface in your browser.

2. Fill in the login form:
   - Select authentication type (Email or Phone)
   - Enter credentials
   - Specify search query (e.g., "python developer")
   - Set maximum applications (1-200)
   - Optionally add answer requirements

3. Click "Start Parsing" to begin the job search and application process.

4. Monitor progress on the dashboard:
   - View current status
   - Check applied/total counts
   - See progress percentage

## Architecture

- **Web Service**: FastAPI backend serving the frontend and API endpoints
- **Worker Service**: Celery worker handling job parsing tasks
- **Redis**: Message queue and result storage
- **Frontend**: Simple HTML/JavaScript interface for job submission and monitoring

## API Endpoints

- `POST /api/jobs/submit/email`: Submit job with email authentication
- `POST /api/jobs/submit/phone`: Submit job with phone authentication
- `GET /api/jobs/{task_id}`: Get job status
- `POST /api/jobs/{task_id}/cancel`: Cancel running job

## Troubleshooting

### Build Issues

- Ensure Docker has sufficient resources
- Check internet connection for dependency downloads

### Runtime Issues

- Verify Redis is running and accessible
- Check logs with `docker-compose logs`
- Ensure configuration files are valid

### Authentication Errors

- Verify credentials are correct
- Check for CAPTCHA or rate limiting on hh.ru
- Ensure account has necessary permissions

## Development

For development setup:

1. Install uv package manager: `pip install uv`
2. Install dependencies: `uv sync`
3. Copy and configure environment: `cp .env.test .env`
4. Run web service: `uv run -m app.main`
5. Run worker in another terminal: `uv run celery -A app.celery_app.celery_app worker --loglevel=info --queues=hh_parsing_queue`
6. Ensure Redis is running locally or via Docker
