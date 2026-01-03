# Simple Drive API

A simple object storage system designed to support multiple backend storage solutions. Built with **FastAPI** and **Python**, it offers a flexible way to store and retrieve binary data.

## Features

-   **Blob Storage**: Store and retrieve binary data (blobs).
-   **Multiple Backends**: Support for various storage backends:
    -   **Database**: Store blobs directly in a PostgreSQL database.
    -   **Local**: Store blobs on the local file system.
    -   **S3**: Store blobs in Amazon S3-compatible storage.
    -   **FTP**: Store blobs on an FTP server.
-   **Metadata Tracking**: Automatically tracks file metadata (size, creation time, original name) in a PostgreSQL database.
-   **Authentication**: Secure API endpoints using Bearer token authentication.
-   **Docker Support**: Containerized deployment with Docker and Docker Compose.

## Tech Stack

-   **Framework**: FastAPI
-   **Language**: Python 3.10+
-   **Database**: PostgreSQL
-   **ORM**: SQLAlchemy (Async)
-   **Migrations**: Alembic
-   **Containerization**: Docker & Docker Compose

## Prerequisites

-   **Python 3.10+**
-   **Docker & Docker Compose** (for containerized deployment)
-   **PostgreSQL** (if running locally without Docker)

## Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Simple-Drive
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    Copy the example environment file and configure it:
    ```bash
    # On Windows (PowerShell)
    copy .env.example .env
    # On macOS/Linux
    cp .env.example .env
    ```
    Update `.env` with your specific configurations (Database credentials, Storage backend choice, Auth token, etc.).

## Database Migration

Initialize the database schema using Alembic:

```bash
alembic upgrade head
```

## Running the Application

### Local Development

Run the API server using Uvicorn:

```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

### Using Docker

Build and start the services:

```bash
docker-compose up -d --build
```

## API Usage

### Authentication
All requests require a Bearer token in the `Authorization` header.
`Authorization: Bearer <YOUR_AUTH_TOKEN>`

### Endpoints

-   **Health Check**:
    -   `GET /health`
    -   Returns the status of the API.

-   **Upload Blob**:
    -   `POST /api/blobs`
    -   Upload a file to the configured storage backend.
    -   **Body**: `multipart/form-data` with a `file` field.

-   **Retrieve Blob**:
    -   `GET /api/blobs/{blob_id}`
    -   Retrieve a stored blob and its metadata.

-   **Root**:
    -   `GET /`
    -   Welcome message.
