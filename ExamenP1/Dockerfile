# Use Python 3.11 slim image
FROM python:3.11-slim AS backend

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    g++ \
    gcc \
    pkg-config \
    sqlite3 \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x (more stable for Next.js)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend
COPY . .

# Install frontend dependencies
WORKDIR /app/agent-ui
RUN pnpm install && pnpm build

WORKDIR /app

# Copy start script and set permissions
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Make start script executable, create tmp directory, set permissions, and create user
RUN mkdir -p tmp && \
    chmod 755 tmp && \
    useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# Instalar Nginx antes de cambiar de usuario
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copiar configuración de Nginx
COPY nginx.conf /app/nginx.conf

USER app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7777
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 3000

# Health check using python
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Run the application
CMD ["/app/start.sh"]
