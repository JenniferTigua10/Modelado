#!/bin/bash
#!/bin/bash

echo "🚀 Iniciando Backend..."
cd backend
node app.js &
cd ..

echo "🌐 Iniciando Frontend..."
cd frontend/taskflow-frontend
npm run serve
