# zenOS — Python 3.14 security lab / CLI image
# Secrets stay out of the image. Pass GITHUB_TOKEN at runtime.

FROM python:3.14-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash zen \
    && mkdir -p /home/zen/.zenOS /config /workspace /app

WORKDIR /app

COPY pyproject.toml requirements.txt README.md ./
COPY zen/ /app/zen/
COPY dex/ /app/dex/
COPY scripts/ /app/scripts/
COPY .env.template /app/.env.template
COPY .cursor/mcp.json.template /app/.cursor/mcp.json.template

# setup.py is an installer script, not setuptools — install deps from requirements.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && chown -R zen:zen /app /home/zen /config /workspace

USER zen

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8080 \
    ZEN_CONFIG_PATH=/config \
    HOME=/home/zen

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT:-8080}/health" || exit 1

CMD ["python", "-m", "zen.lab"]
