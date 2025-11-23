# Grapegram Backend

Backend for Grapegram messenger - a Domain-Driven Design (DDD) application built with Python, featuring clean architecture principles and async-first design.

## Tech Stack

<div align="center">
    <a href="https://www.python.org/" target="_blank">
        <img src="https://img.shields.io/badge/-Python_3.13-black?style=for-the-badge&logoColor=white&logo=python&color=9C36CF" alt="Python" />
    </a>
    <a href="https://litestar.dev/" target="_blank">
        <img src="https://img.shields.io/badge/-Litestar-black?style=for-the-badge&logoColor=white&logo=litestar&color=212121" alt="Litestar" />
    </a>
    <a href="https://www.sqlalchemy.org/" target="_blank">
        <img src="https://img.shields.io/badge/-SQLAlchemy-black?style=for-the-badge&logoColor=white&logo=sqlalchemy&color=9C36CF" alt="SQLAlchemy" />
    </a>
    <a href="https://www.postgresql.org/" target="_blank">
        <img src="https://img.shields.io/badge/-PostgreSQL-black?style=for-the-badge&logoColor=white&logo=postgresql&color=212121" alt="PostgreSQL" />
    </a>
    <a href="https://redis.io/" target="_blank">
        <img src="https://img.shields.io/badge/-Redis-black?style=for-the-badge&logoColor=white&logo=redis&color=9C36CF" alt="Redis" />
    </a>
    <a href="https://pydantic.dev/" target="_blank">
        <img src="https://img.shields.io/badge/-Pydantic-black?style=for-the-badge&logoColor=white&logo=pydantic&color=212121" alt="Pydantic" />
    </a>
    <a href="https://jwt.io/" target="_blank">
        <img src="https://img.shields.io/badge/-JWT-black?style=for-the-badge&logoColor=white&logo=jsonwebtokens&color=9C36CF" alt="JWT" />
    </a>
</div>

## Dev Instruments

<div align="center">
    <a href="https://docs.astral.sh/uv/" target="_blank">
        <img src="https://img.shields.io/badge/-uv-black?style=for-the-badge&logoColor=white&logo=uv&color=9C36CF" alt="uv" />
    </a>
    <a href="https://docs.astral.sh/ruff/" target="_blank">
        <img src="https://img.shields.io/badge/-Ruff-black?style=for-the-badge&logoColor=white&logo=ruff&color=212121" alt="Ruff" />
    </a>
    <a href="https://mypy-lang.org/" target="_blank">
        <img src="https://img.shields.io/badge/-Mypy-black?style=for-the-badge&logoColor=white&logo=python&color=9C36CF" alt="Mypy" />
    </a>
    <a href="https://docs.pytest.org/" target="_blank">
        <img src="https://img.shields.io/badge/-Pytest-black?style=for-the-badge&logoColor=white&logo=pytest&color=212121" alt="Pytest" />
    </a>
    <a href="https://alembic.sqlalchemy.org/" target="_blank">
        <img src="https://img.shields.io/badge/-Alembic-black?style=for-the-badge&logoColor=white&logo=alembic&color=9C36CF" alt="Alembic" />
    </a>
    <a href="https://www.docker.com/" target="_blank">
        <img src="https://img.shields.io/badge/-Docker-black?style=for-the-badge&logoColor=white&logo=docker&color=212121" alt="Docker" />
    </a>
    <a href="https://pre-commit.com/" target="_blank">
        <img src="https://img.shields.io/badge/-Pre--commit-black?style=for-the-badge&logoColor=white&logo=precommit&color=9C36CF" alt="Pre-commit" />
    </a>
</div>

## 🚀 Features

- **Domain-Driven Design**: Clean separation of concerns with domain, application, and infrastructure layers
- **Async-First**: Built on Litestar (async web framework) and async database drivers
- **Type-Safe**: Full type hints with mypy validation
- **Event-Driven**: Event bus integration with FastStream and Redis
- **Real-time**: WebSocket support for live updates
- **IAM Module**: Identity and Access Management with JWT authentication

## 📋 Prerequisites

- Make
- Python 3.13+
- Docker & Docker Compose (for containerized setup)

## 🛠️ Installation

### Using uv (recommended)

```bash
# Install dependencies
uv sync

# Activate virtual environment
. ./.venv/bin/activate
```

## 🚦 Quick Start

### Development with Docker

```bash
# Start all services
make up

# Start in background
make up_bg

# Stop services
make down
```

The API will be available at `http://localhost:8000`

## 🔧 Development

### Database Migrations

```bash
# Create a new migration
make migration_create MESSAGE="your migration description"

# Apply migrations
make migrate
```

### Code Quality

```bash
# Run linter
make lint

# Format code
make format

# Run tests
make test
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🔑 Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
```

## 🧪 Testing

```bash
# Run all tests
make test
```

## 📁 Project Structure

```
ddd-backend/
├── src/
│   ├── app/           # Application setup (DI, DB, settings)
│   ├── core/          # Core bounded contexts (Chat, etc.)
│   ├── generic/       # Generic bounded contexts (IAM, etc.)
│   ├── supporting/    # Supporting bounded contexts
│   └── migrations/    # Database migrations
├── seedwork/          # Shared kernel (base classes, utilities)
├── containers/        # Docker configurations
└── scripts/           # Build and deployment scripts
```

## 🏗️ Architecture

This project follows Domain-Driven Design principles:

- **Domain Layer**: Aggregates, entities, value objects, domain events, and business rules
- **Application Layer**: Use cases, commands, queries, and event handlers
- **Infrastructure Layer**: Repository implementations, external services
- **Presentation Layer**: API endpoints, WebSocket handlers

### Key Patterns

- **Result Container**: Error handling without exceptions using `returns` library
- **Business Rules**: Explicit domain rules as separate classes
- **Event Sourcing**: Domain events for state changes
- **Dependency Injection**: Using `dishka` for clean dependency management

## 📚 Documentation

- [Agent Guidelines](AGENTS.md) - Guidelines for LLM agents working on this codebase
- [Architecture Overview](https://grapegram.github.io/docs/) - Detailed architecture documentation
