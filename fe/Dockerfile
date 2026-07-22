# Multi-stage build: compile the Vite app, then serve the static bundle via Nginx.
FROM docker.io/library/node:20-slim AS build

WORKDIR /app

# Install dependencies against the lockfile for reproducible builds.
COPY package.json package-lock.json ./
RUN npm ci

# Build the production bundle into /app/dist.
COPY . .
RUN npm run build

# Runtime stage: a tiny Nginx image serving the static files and proxying /api.
FROM docker.io/library/nginx:1.27-alpine AS runtime

# SPA-aware config with an /api reverse proxy to the Flask service.
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
