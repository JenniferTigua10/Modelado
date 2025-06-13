# Usar una imagen base de Node.js para la etapa de construcción
FROM node:18-alpine AS build

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json (si existe)
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar el código fuente (excepto node_modules que ya está en .dockerignore)
COPY . .

# Asegurar que las variables de entorno estén disponibles durante el build
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_KEY
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_KEY=$VITE_SUPABASE_KEY

# Mostrar las variables de entorno para debugging (sin mostrar valores sensibles)
RUN echo "Building with environment variables set"

# Construir la aplicación
RUN npm run build

# Verificar que el build se haya creado correctamente
RUN ls -la /app/dist

# Etapa de producción con Nginx
FROM nginx:alpine

# Eliminar la configuración por defecto de nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar los archivos construidos desde la etapa de build
COPY --from=build /app/dist /usr/share/nginx/html

# Verificar que los archivos se copiaron correctamente
RUN ls -la /usr/share/nginx/html

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Crear directorio de logs
RUN mkdir -p /var/log/nginx

# Exponer el puerto 8080 (requerido por Cloud Run)
EXPOSE 8080

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
