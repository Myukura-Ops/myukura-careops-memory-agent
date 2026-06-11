# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
# Copy package files
COPY package*.json ./
# Install dependencies
RUN npm install
# Copy the rest of the application
COPY . .
# Set build arguments for API URL substitution during Vite build
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
# Build the application
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
# Copy static files from builder
COPY --from=builder /app/dist /usr/share/nginx/html
# Cloud Run dynamically sets the PORT environment variable
ENV PORT=80
# Update the default nginx listen port at startup to match Cloud Run's PORT, then start nginx
CMD sed -i -e 's/listen.*/listen '"$PORT"';/' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
