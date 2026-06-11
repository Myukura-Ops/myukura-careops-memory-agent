FROM python:3.11-slim

# Node.js runtime for the official MongoDB MCP Server (spawned over stdio,
# always in --readOnly mode, used for operational memory reads).
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g mongodb-mcp-server@1.12.0 \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
