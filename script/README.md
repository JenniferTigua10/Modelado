# Azure VM Creator v2.0.0 🚀

Una herramienta profesional desarrollada en Python para crear máquinas virtuales en Azure con interfaz interactiva y configuración avanzada.

## ✨ Características Principales

- 🎯 **Interfaz Interactiva**: Menú profesional con guía paso a paso
- ⚙️ **Configuración Flexible**: Soporte para archivos JSON y argumentos CLI
- 🔒 **Seguridad Integrada**: Configuración automática de NSG y reglas de firewall
- 📋 **Logging Avanzado**: Sistema de logs detallado con múltiples niveles
- 🎛️ **Modo Dry-Run**: Vista previa de configuración sin crear recursos
- 🏷️ **Tags Automáticos**: Etiquetado inteligente para organización
- 🔄 **Manejo de Errores**: Recuperación robusta y mensajes informativos

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Navegar al directorio del proyecto
cd script-azure

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Autenticarse en Azure
az login
```

### 2. Configurar Subscription ID

```bash
# Opción 1: Variable de entorno (recomendado)
export AZURE_SUBSCRIPTION_ID="tu-subscription-id-aqui"

# Opción 2: Obtener ID automáticamente
export AZURE_SUBSCRIPTION_ID=$(az account show --query id --output tsv)
```

### 3. Ejecutar la Herramienta

#### Modo Interactivo (Recomendado)
```bash
python create_vm.py
```

#### Línea de Comandos
```bash
# Creación básica
python create_vm.py --vm-name mi-servidor --location "West Europe"

# Con configuración avanzada
python create_vm.py --config config.json --log-level DEBUG

# Vista previa sin crear recursos
python create_vm.py --dry-run --vm-name test-vm
```

## 📋 Menú Interactivo

El script incluye un menú profesional con las siguientes opciones:

1. **🆕 Crear nueva máquina virtual** - Configuración rápida con valores por defecto
2. **⚙️ Crear VM con configuración personalizada** - Asistente interactivo completo
3. **📄 Generar archivo de configuración** - Crear plantilla JSON personalizable
4. **🔍 Vista previa de configuración** - Modo dry-run para validar configuración
5. **📚 Mostrar ejemplos de uso** - Guía de comandos CLI
6. **❓ Ayuda y documentación** - Información detallada
7. **🚪 Salir** - Terminar la aplicación

## ⚙️ Configuración

### Generar Configuración Base

```bash
python create_vm.py --generate-config mi-config.json
```

### Ejemplo de Configuración JSON

```json
{
  "vm_name": "servidor-web-prod",
  "resource_group": "rg-webapp",
  "location": "West Europe",
  "vm_size": "Standard_D2s_v3",
  "admin_username": "webadmin",
  "image": {
    "publisher": "Canonical",
    "offer": "0001-com-ubuntu-server-focal",
    "sku": "20_04-lts-gen2",
    "version": "latest"
  },
  "network": {
    "vnet_name": "vnet-webapp",
    "vnet_address_space": "10.1.0.0/16",
    "subnet_name": "subnet-web",
    "subnet_address_prefix": "10.1.1.0/24"
  },
  "security": {
    "ssh_port": 2222,
    "allowed_ssh_sources": ["203.0.113.0/24"]
  },
  "tags": {
    "Environment": "Production",
    "Department": "IT"
  }
}
```

### Argumentos de Línea de Comandos

```bash
Argumentos principales:
  --vm-name             Nombre de la máquina virtual
  --resource-group      Nombre del grupo de recursos
  --location            Ubicación de Azure
  --vm-size             Tamaño de la VM
  --admin-user          Usuario administrador

Configuración:
  --config, -c          Archivo de configuración JSON
  --subscription-id     Azure Subscription ID
  --log-level          Nivel de logging (DEBUG, INFO, WARNING, ERROR)

Utilidades:
  --dry-run            Mostrar configuración sin crear recursos
  --generate-config    Generar archivo de configuración de ejemplo
  --help              Mostrar ayuda completa
```

## 🏗️ Recursos Creados

La herramienta crea automáticamente:

- ✅ **Grupo de recursos** - Contenedor lógico
- ✅ **Red virtual (VNet)** - Red privada
- ✅ **Subred** - Segmento de red
- ✅ **IP pública** - Acceso desde Internet
- ✅ **Grupo de seguridad (NSG)** - Firewall
- ✅ **Interfaz de red (NIC)** - Conexión de red
- ✅ **Máquina virtual** - Recurso principal

## 🔧 Tamaños de VM Soportados

| Tamaño | vCPUs | RAM | Uso Recomendado |
|--------|-------|-----|-----------------|
| Standard_B1s | 1 | 1GB | Desarrollo, testing |
| Standard_B2s | 2 | 4GB | Aplicaciones ligeras |
| Standard_D2s_v3 | 2 | 8GB | Propósito general |
| Standard_D4s_v3 | 4 | 16GB | Aplicaciones intensivas |

## 🌍 Ubicaciones Soportadas

- **Estados Unidos**: East US, West US, Central US
- **Europa**: West Europe, North Europe, UK South
- **Asia**: Southeast Asia, East Asia, Japan East
- **Otras**: Brazil South, Australia East, Canada Central

## 🚨 Solución de Problemas

### Errores Comunes

#### Error de Autenticación
```bash
az login
az account show
```

#### Subscription ID No Encontrado
```bash
export AZURE_SUBSCRIPTION_ID=$(az account show --query id --output tsv)
```

#### Error de Cuota
- Verificar cuotas en Azure Portal
- Cambiar a región diferente
- Reducir tamaño de VM

## 📝 Notas Importantes

- ⚠️ **Costos**: Las VMs generan costos por hora
- 🔐 **Seguridad**: Cambie contraseñas por defecto
- 📋 **Límites**: Verifique cuotas de suscripción
- 🏷️ **Organización**: Use tags consistentes

---

**Desarrollado por**: Andres  
**Versión**: 2.0.0  
**Fecha**: 6 de junio de 2025
