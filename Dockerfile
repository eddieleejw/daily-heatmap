FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

