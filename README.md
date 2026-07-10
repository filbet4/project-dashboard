# Project Dashboard API

A backend web service built with **FastAPI** that allows users to create collaborative projects, upload documents, and invite other users to work together.

The application was developed as a learning project to demonstrate modern backend development using Python, REST APIs, PostgreSQL, Docker and CI.

---

# Features

### User Authentication

- User registration
- User login
- JWT authentication
- Password hashing with bcrypt

---

### Project Management

- Create a project
- List projects
- View project details
- Update project information
- Delete projects (Owner only)

---

### Document Management

- Upload PDF, DOC and DOCX files
- Download documents
- List project documents
- Delete uploaded documents

---

### Collaboration

- Invite users to projects
- Accept invitations
- Owner and Participant roles
- Authorization based on project membership

---

### Database

- PostgreSQL
- SQLAlchemy ORM
- Automatic table creation

---

### Docker

- Dockerfile
- Docker Compose
- Separate FastAPI and PostgreSQL containers

---

### Continuous Integration

- GitHub Actions
- Automatic dependency installation
- Automated integration tests
- Docker image build verification

---

# Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Programming language |
| FastAPI | REST API framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| Pydantic | Data validation |
| JWT | Authentication |
| Docker | Containerization |
| GitHub Actions | Continuous Integration |
| Requests | Integration testing |

---

# Project Structure

```text
project-dashboard/

├── app/
│   ├── auth.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   ├── schemas.py
│   └── routes/
│       ├── users.py
│       ├── projects.py
│       ├── documents.py
│       └── members.py
│
├── uploads/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py
│
├── test_phase3.py
├── test_phase4.py
├── test_phase5.py
│
└── README.md
```

---

# Architecture

```
Client

↓

FastAPI

↓

Routers

↓

Dependencies

↓

SQLAlchemy ORM

↓

PostgreSQL
```

---

# Running Locally

## Clone repository

```bash
git clone <repository-url>
cd project-dashboard
```

## Create virtual environment

```bash
python -m venv venv
```

Activate it.

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configure environment variables

Create a `.env` file.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/project_dashboard

SECRET_KEY=your-secret-key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Run application

```bash
python main.py
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

# Running with Docker

Build containers

```bash
docker compose up --build
```

Next runs

```bash
docker compose up
```

Swagger

```
http://localhost:8000/docs
```

Stop containers

```bash
docker compose down
```

---

# Running Tests

Phase 3

```bash
python test_phase3.py
```

Phase 4

```bash
python test_phase4.py
```

Phase 5

```bash
python test_phase5.py
```

---

# API Documentation

Interactive Swagger documentation:

```
http://localhost:8000/docs
```

---

# Future Improvements

- Refresh Tokens
- Alembic database migrations
- Cloud file storage (AWS S3)
- Email invitations
- Pagination
- Search functionality
- Unit tests with pytest
- Kubernetes deployment

---

# Author

Developed by **Darek Bętkowski**

Project created for backend learning using FastAPI, PostgreSQL, Docker and GitHub Actions.