#!/bin/bash

# Startup script for Cloud Run
set -e

echo "🚀 Starting Agent Playground..."
echo "Ports: Backend ${PORT:-7777}, Frontend 3000"
echo "Python version: $(python --version)"

# Check if tmp directory exists and create if not
if [ ! -d "tmp" ]; then
    echo "📁 Creating tmp directory..."
    mkdir -p tmp
    chmod 755 tmp
fi

# Asegurar que el directorio tmp existe y tiene permisos antes de iniciar el backend
if [ ! -d "/app/tmp" ]; then
    echo "📁 Creando directorio /app/tmp..."
    mkdir -p /app/tmp
    chmod 777 /app/tmp
fi

# Initialize database if needed
echo "🗄️ Initializing database..."
python -c "
import sqlite3
import os
db_path = 'tmp/agents.db'
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.close()
    print('Database initialized')
else:
    print('Database already exists')
"

# Iniciar Nginx en background
nginx -c /app/nginx.conf &

# Start the backend application
echo "🌟 Starting backend Uvicorn server on port ${PORT:-7777}..."
python -m uvicorn playground:app \
    --host 0.0.0.0 \
    --port ${PORT:-7777} \
    --log-level info \
    --access-log \
    --timeout-keep-alive 5 \
    --timeout-graceful-shutdown 30 &

# Navigate to the frontend directory and start the frontend application
echo "▶️ Starting frontend Next.js application on port 3000..."
cd /app/agent-ui
pnpm start --port 3000 &

# Wait for all background processes to complete
wait
