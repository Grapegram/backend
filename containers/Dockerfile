# Set python version
ARG BASE_CONTAINER=python:3.13-slim-bookworm

# Base stage - common for both dev and prod
FROM --platform=linux/amd64 $BASE_CONTAINER as base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# dont write pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# dont buffer to stdout/stderr
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get upgrade

# Make a directory for app
WORKDIR /app

# Install dependencies
COPY ./uv.lock ./pyproject.toml ./
RUN touch README.md && uv venv

# Development stage
FROM base as development
RUN uv sync
CMD ["uv", "run", "serve"]

# Production stage
FROM base as production
RUN uv sync --no-dev
COPY . .
CMD ["uv", "run", "serve"]
