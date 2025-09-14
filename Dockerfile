# Multi-stage build for efficient image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY pyproject.toml .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash zen && \
    mkdir -p /home/zen/.zenOS /config /workspace && \
    chown -R zen:zen /home/zen /config /workspace

# Set working directory
WORKDIR /app

# Copy wheels and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

# Copy application code
COPY --chown=zen:zen zen/ /app/zen/
COPY --chown=zen:zen agents/ /app/agents/
COPY --chown=zen:zen modules/ /app/modules/
COPY --chown=zen:zen configs/ /app/configs/

# Switch to non-root user
USER zen

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ZEN_CONFIG_PATH=/config \
    HOME=/home/zen

# Default command
CMD ["python", "-m", "zen.cli"]
