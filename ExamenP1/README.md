# Agent Playground - Cloud Run Deployment

## Descripción
Una aplicación de playground para agentes de IA con capacidades web y financieras.

## Configuración para Cloud Run

### Prerrequisitos
- Tener un proyecto de Google Cloud configurado
- Cloud Build API habilitada
- Cloud Run API habilitada
- Artifact Registry API habilitada

### Despliegue

1. **Clonar o preparar el código:**
   ```bash
   # Asegúrate de estar en el directorio del proyecto
   cd /path/to/ExamenP1-Modelado
   ```

2. **Configurar el proyecto:**
   ```bash
   # Reemplaza YOUR_PROJECT_ID con tu ID de proyecto real
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Crear repositorio de Artifact Registry (si no existe):**
   ```bash
   gcloud artifacts repositories create agent-playground-repo \
       --repository-format=docker \
       --location=us-central1 \
       --description="Repository for agent playground"
   ```

4. **Desplegar usando Cloud Build:**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

### Variables de Entorno
- `PORT=7777` - Puerto en el que la aplicación escucha
- `PYTHONUNBUFFERED=1` - Para logging en tiempo real

### Endpoints
- `/health` - Health check endpoint
- `/` - Interfaz principal del playground

### Troubleshooting

Si tienes problemas con el despliegue:

1. **Verificar logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=examenp1-modelado" --limit 50
   ```

2. **Verificar configuración del puerto:**
   - La aplicación debe escuchar en el puerto especificado por la variable `PORT`
   - Cloud Run debe estar configurado para el mismo puerto

3. **Verificar timeouts:**
   - El contenedor tiene 10 minutos para iniciar
   - Increase el timeout si es necesario

### Arquitectura
- **Framework:** FastAPI con Uvicorn
- **Agentes:** Web Agent (DuckDuckGo) y Finance Agent (YFinance)
- **Base de datos:** SQLite local
- **LLM:** Groq (Llama 3)

### Notas Importantes
- El archivo `tmp/agents.db` se crea automáticamente
- La API key de Groq está hardcodeada (considera usar Secret Manager en producción)
- La aplicación corre como usuario no-root por seguridad
