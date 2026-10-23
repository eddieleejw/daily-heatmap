FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY src/ ./src/
COPY configs/ ./configs/
RUN uv sync --locked --no-dev

EXPOSE 8800

CMD ["python", "-m", "heatmap.api.app"]
