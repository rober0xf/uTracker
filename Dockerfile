FROM python:3.13-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

WORKDIR /app
RUN uv sync --frozen --no-cache

CMD ["./.venv/bin/uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]