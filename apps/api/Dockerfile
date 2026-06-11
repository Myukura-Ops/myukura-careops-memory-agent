# ── Stage 1: Builder ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
       | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
       > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g mongodb-mcp-server@1.12.0 \
    && apt-get purge -y curl gnupg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────
FROM python:3.11-slim

# Install Node.js runtime (required for mongodb-mcp-server at runtime)
COPY --from=builder /usr/bin/node /usr/bin/node
COPY --from=builder /usr/lib/node_modules /usr/lib/node_modules
COPY --from=builder /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/lib/node_modules/npm/bin/npm-cli.js /usr/bin/npm \
    && ln -sf /usr/bin/node /usr/bin/nodejs \
    && ln -sf /usr/local/lib/node_modules/mongodb-mcp-server/dist/index.js /usr/local/bin/mongodb-mcp-server

# Copy Python dependencies
COPY --from=builder /build/deps /usr/local/lib/python3.11/site-packages

# Create non-root user
RUN groupadd --system appuser && useradd --system --gid appuser appuser

WORKDIR /app
COPY ./app ./app

# Switch to non-root user
USER appuser

EXPOSE 8080
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
