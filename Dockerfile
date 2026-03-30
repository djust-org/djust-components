# Dockerfile for components.djust.org
# Builds djust-components from source and runs the component_showcase Django app

FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install build tools for building djust-components wheel
RUN pip install --no-cache-dir build

# Copy project files needed to build the wheel
COPY pyproject.toml README.md CHANGELOG.md ./
COPY src/ ./src/

# Build djust-components wheel from source
RUN python -m build --wheel --outdir /tmp/wheels/

# Copy production requirements and pre-built djust wheel (from CI)
COPY requirements-prod.txt ./
COPY wheel[s]/ ./wheels/

# Install all dependencies
# Order: prod requirements first (pulls djust from PyPI or /wheels), then local wheel
RUN pip install --no-cache-dir -r requirements-prod.txt \
    && if ls /wheels/*.whl 1>/dev/null 2>&1; then pip install --no-cache-dir /wheels/*.whl; fi \
    && pip install --no-cache-dir /tmp/wheels/djust_components*.whl \
    && rm -rf /wheels /tmp/wheels

# Copy the showcase application
COPY component_showcase/ ./component_showcase/
COPY components/ ./components/
COPY manage.py ./

# Pre-collect static files during build
RUN DEBUG=False python manage.py collectstatic --noinput

# Copy entrypoint
COPY entrypoint.sh ./
RUN chmod +x /app/entrypoint.sh

# Create necessary directories and non-root user
RUN mkdir -p /app/staticfiles \
    && useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "component_showcase.asgi:application"]
