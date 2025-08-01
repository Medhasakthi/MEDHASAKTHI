# MEDHASAKTHI Frontend Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Set environment variables for build
ENV HUSKY=0
ENV NODE_OPTIONS=--max-old-space-size=4096
ENV GENERATE_SOURCEMAP=false
ENV REACT_APP_API_URL=/api
ENV REACT_APP_APP_NAME=MEDHASAKTHI
ENV REACT_APP_STUDENT_URL=https://student.medhasakthi.com
ENV REACT_APP_TEACHER_URL=https://teacher.medhasakthi.com
ENV REACT_APP_ADMIN_URL=https://admin.medhasakthi.com
ENV REACT_APP_LEARN_URL=https://learn.medhasakthi.com

# Install dependencies first
COPY package*.json ./
RUN npm cache clean --force && \
    npm install --legacy-peer-deps --no-audit --no-fund --production=false

# Copy source code
COPY . .

# Create environment file for build
RUN echo "REACT_APP_API_URL=/api" > .env.local && \
    echo "REACT_APP_APP_NAME=MEDHASAKTHI" >> .env.local && \
    echo "REACT_APP_STUDENT_URL=https://student.medhasakthi.com" >> .env.local && \
    echo "REACT_APP_TEACHER_URL=https://teacher.medhasakthi.com" >> .env.local && \
    echo "REACT_APP_ADMIN_URL=https://admin.medhasakthi.com" >> .env.local && \
    echo "REACT_APP_LEARN_URL=https://learn.medhasakthi.com" >> .env.local

# Build the application with better error handling
RUN set -e && \
    echo "Starting React build..." && \
    npm run build:production && \
    echo "Build completed successfully" && \
    ls -la build/

# Stage 2: Production stage
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set permissions for nginx
RUN chown -R nginx:nginx /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
