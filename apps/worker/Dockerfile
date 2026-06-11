# ── Stage 1: Builder ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────
FROM python:3.11-slim

# Copy Python dependencies
COPY --from=builder /build/deps /usr/local/lib/python3.11/site-packages

# Create non-root user
RUN groupadd --system appuser && useradd --system --gid appuser appuser

WORKDIR /app
COPY ./app ./app

# Switch to non-root user
USER appuser

EXPOSE 8081
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
