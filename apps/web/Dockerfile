# ── Stage 1: Build ───────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# ── Stage 2: Serve ───────────────────────────────────────────────
FROM nginx:alpine

# Copy static files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run dynamically sets the PORT environment variable
ENV PORT=80

# Update the default nginx listen port at startup to match Cloud Run's PORT, then start nginx
CMD sed -i -e 's/listen.*/listen '"$PORT"';/' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
