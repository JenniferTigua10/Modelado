#!/usr/bin/env python3
"""
Azure Virtual Machine Creator - Herramienta profesional para crear VMs en Azure

Este script proporciona una interfaz robusta y profesional para crear máquinas virtuales
en Azure con todas las dependencias necesarias (redes, seguridad, etc.).

Autor: Andres
Versión: 2.0.0
Fecha: 2025-06-06
"""

import os
import sys
import json
import logging
import argparse
import getpass
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.core.exceptions import AzureError

# Configuración de logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configurar el sistema de logging (solo consola para producción minimalista)"""
    logger = logging.getLogger("azure_vm_creator")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger


class VMConfig:
    """Clase para manejar la configuración de la VM"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger("azure_vm_creator.config")
        self.config = self._load_config(config_file) if config_file else self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'vm_name': 'azure-vm-prod',
            'resource_group': 'rg-azure-vm',
            'location': 'East US',
            'vm_size': 'Standard_B2s',
            'admin_username': 'azureuser',
            'os_type': 'linux',
            'image': {
                'publisher': 'Canonical',
                'offer': '0001-com-ubuntu-server-focal',
                'sku': '20_04-lts-gen2',
                'version': 'latest'
            },
            'network': {
                'vnet_name': 'vnet-azure-vm',
                'vnet_address_space': '10.0.0.0/16',
                'subnet_name': 'subnet-default',
                'subnet_address_prefix': '10.0.0.0/24',
                'public_ip_name': 'ip-azure-vm',
                'nsg_name': 'nsg-azure-vm',
                'nic_name': 'nic-azure-vm'
            },
            'disk': {
                'os_disk_size_gb': 30,
                'storage_account_type': 'Premium_LRS'
            },
            'security': {
                'ssh_port': 22,
                'allowed_ssh_sources': ['*']
            },
            'tags': {
                'Environment': 'Production',
                'CreatedBy': 'AzureVMCreator',
                'Project': 'Infrastructure'
            }
        }
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Cargar configuración desde archivo JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"Configuración cargada desde {config_file}")
            return config
        except FileNotFoundError:
            self.logger.warning(f"Archivo de configuración {config_file} no encontrado. Usando configuración por defecto.")
            return self._default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear JSON: {e}")
            raise
    
    def validate(self) -> bool:
        """Validar la configuración"""
        required_fields = ['vm_name', 'resource_group', 'location', 'admin_username']
        
        for field in required_fields:
            if not self.config.get(field):
                self.logger.error(f"Campo requerido faltante: {field}")
                return False
        
        # Validar nombre de VM (Azure naming conventions)
        vm_name = self.config['vm_name']
        if not (1 <= len(vm_name) <= 64 and vm_name.replace('-', '').replace('_', '').isalnum()):
            self.logger.error("Nombre de VM inválido. Debe tener 1-64 caracteres alfanuméricos, guiones o guiones bajos.")
            return False
        
        self.logger.info("Configuración validada exitosamente")
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        return self.config.get(key, default)


class AzureVMCreator:
    """Clase principal para crear máquinas virtuales en Azure"""
    
    def __init__(self, subscription_id: str, config: VMConfig):
        self.subscription_id = subscription_id
        self.config = config
        self.logger = logging.getLogger("azure_vm_creator.main")
        
        try:
            self.credential = DefaultAzureCredential()
            self.resource_client = ResourceManagementClient(self.credential, subscription_id)
            self.compute_client = ComputeManagementClient(self.credential, subscription_id)
            self.network_client = NetworkManagementClient(self.credential, subscription_id)
            
            self.logger.info("Clientes de Azure inicializados correctamente")
        except Exception as e:
            self.logger.error(f"Error al inicializar clientes de Azure: {e}")
            raise
    
    def _add_tags(self, params: Dict[str, Any]) -> None:
        """Añadir tags a los recursos"""
        tags = self.config.get('tags', {})
        tags['CreatedAt'] = datetime.now().isoformat()
        if tags:
            params['tags'] = tags
    
    def create_resource_group(self, resource_group_name: str, location: str) -> Any:
        """Crear grupo de recursos con manejo de errores mejorado"""
        self.logger.info(f"Creando grupo de recursos: {resource_group_name} en {location}")
        
        try:
            # Verificar si ya existe
            try:
                existing_rg = self.resource_client.resource_groups.get(resource_group_name)
                self.logger.info(f"Grupo de recursos {resource_group_name} ya existe")
                return existing_rg
            except:
                pass  # No existe, continuamos con la creación
            
            rg_params = {"location": location}
            self._add_tags(rg_params)
            
            rg_result = self.resource_client.resource_groups.create_or_update(
                resource_group_name, rg_params
            )
            
            self.logger.info(f"✓ Grupo de recursos creado: {rg_result.name}")
            return rg_result
            
        except AzureError as e:
            self.logger.error(f"Error al crear grupo de recursos: {e}")
            raise
    
    def create_virtual_network(self, resource_group_name: str, vnet_name: str, location: str) -> Any:
        """Crear red virtual con configuración avanzada"""
        self.logger.info(f"Creando red virtual: {vnet_name}")
        
        try:
            network_config = self.config.get('network', {})
            
            vnet_params = {
                'location': location,
                'address_space': {
                    'address_prefixes': [network_config.get('vnet_address_space', '10.0.0.0/16')]
                }
            }
            self._add_tags(vnet_params)
            
            creation_result = self.network_client.virtual_networks.begin_create_or_update(
                resource_group_name, vnet_name, vnet_params
            )
            
            vnet_result = creation_result.result()
            self.logger.info(f"✓ Red virtual creada: {vnet_result.name}")
            return vnet_result
            
        except AzureError as e:
            self.logger.error(f"Error al crear red virtual: {e}")
            raise
    
    def create_subnet(self, resource_group_name: str, vnet_name: str, subnet_name: str) -> Any:
        """Crear subred con configuración personalizable"""
        self.logger.info(f"Creando subred: {subnet_name}")
        
        try:
            network_config = self.config.get('network', {})
            
            subnet_params = {
                'address_prefix': network_config.get('subnet_address_prefix', '10.0.0.0/24')
            }
            
            creation_result = self.network_client.subnets.begin_create_or_update(
                resource_group_name, vnet_name, subnet_name, subnet_params
            )
            
            subnet_result = creation_result.result()
            self.logger.info(f"✓ Subred creada: {subnet_result.name}")
            return subnet_result
            
        except AzureError as e:
            self.logger.error(f"Error al crear subred: {e}")
            raise
    
    def create_public_ip(self, resource_group_name: str, ip_name: str, location: str) -> Any:
        """Crear IP pública con configuración estática"""
        self.logger.info(f"Creando IP pública: {ip_name}")
        
        try:
            public_ip_params = {
                'location': location,
                'public_ip_allocation_method': 'Static',
                'sku': {'name': 'Standard'}
            }
            self._add_tags(public_ip_params)
            
            creation_result = self.network_client.public_ip_addresses.begin_create_or_update(
                resource_group_name, ip_name, public_ip_params
            )
            
            ip_result = creation_result.result()
            self.logger.info(f"✓ IP pública creada: {ip_result.name}")
            return ip_result
            
        except AzureError as e:
            self.logger.error(f"Error al crear IP pública: {e}")
            raise
    
    def create_network_security_group(self, resource_group_name: str, nsg_name: str, location: str) -> Any:
        """Crear grupo de seguridad de red con reglas configurables"""
        self.logger.info(f"Creando grupo de seguridad: {nsg_name}")
        
        try:
            security_config = self.config.get('security', {})
            ssh_port = security_config.get('ssh_port', 22)
            allowed_sources = security_config.get('allowed_ssh_sources', ['*'])
            
            security_rules = []
            
            # Regla SSH
            for i, source in enumerate(allowed_sources):
                security_rules.append({
                    'name': f'SSH_{i+1}',
                    'protocol': 'Tcp',
                    'source_port_range': '*',
                    'destination_port_range': str(ssh_port),
                    'source_address_prefix': source,
                    'destination_address_prefix': '*',
                    'access': 'Allow',
                    'priority': 1000 + i,
                    'direction': 'Inbound'
                })
            
            # Regla para denegar todo lo demás
            security_rules.append({
                'name': 'DenyAllInbound',
                'protocol': '*',
                'source_port_range': '*',
                'destination_port_range': '*',
                'source_address_prefix': '*',
                'destination_address_prefix': '*',
                'access': 'Deny',
                'priority': 4096,
                'direction': 'Inbound'
            })
            
            nsg_params = {
                'location': location,
                'security_rules': security_rules
            }
            self._add_tags(nsg_params)
            
            creation_result = self.network_client.network_security_groups.begin_create_or_update(
                resource_group_name, nsg_name, nsg_params
            )
            
            nsg_result = creation_result.result()
            self.logger.info(f"✓ Grupo de seguridad creado: {nsg_result.name}")
            return nsg_result
            
        except AzureError as e:
            self.logger.error(f"Error al crear grupo de seguridad: {e}")
            raise
    
    def create_network_interface(self, resource_group_name: str, nic_name: str, location: str, 
                                subnet_id: str, public_ip_id: str, nsg_id: str) -> Any:
        """Crear interfaz de red con configuración avanzada"""
        self.logger.info(f"Creando interfaz de red: {nic_name}")
        
        try:
            nic_params = {
                'location': location,
                'ip_configurations': [{
                    'name': 'default',
                    'subnet': {'id': subnet_id},
                    'public_ip_address': {'id': public_ip_id},
                    'private_ip_allocation_method': 'Dynamic'
                }],
                'network_security_group': {'id': nsg_id}
            }
            self._add_tags(nic_params)
            
            creation_result = self.network_client.network_interfaces.begin_create_or_update(
                resource_group_name, nic_name, nic_params
            )
            
            nic_result = creation_result.result()
            self.logger.info(f"✓ Interfaz de red creada: {nic_result.name}")
            return nic_result
            
        except AzureError as e:
            self.logger.error(f"Error al crear interfaz de red: {e}")
            raise
    
    def create_virtual_machine(self, resource_group_name: str, vm_name: str, location: str, 
                              nic_id: str, admin_username: str, admin_password: str) -> Any:
        """Crear máquina virtual con configuración completa"""
        self.logger.info(f"Creando máquina virtual: {vm_name}")
        
        try:
            image_config = self.config.get('image', {})
            disk_config = self.config.get('disk', {})
            
            vm_params = {
                'location': location,
                'os_profile': {
                    'computer_name': vm_name,
                    'admin_username': admin_username,
                    'admin_password': admin_password,
                    'disable_password_authentication': False
                },
                'hardware_profile': {
                    'vm_size': self.config.get('vm_size', 'Standard_B2s')
                },
                'storage_profile': {
                    'image_reference': {
                        'publisher': image_config.get('publisher', 'Canonical'),
                        'offer': image_config.get('offer', '0001-com-ubuntu-server-focal'),
                        'sku': image_config.get('sku', '20_04-lts-gen2'),
                        'version': image_config.get('version', 'latest')
                    },
                    'os_disk': {
                        'caching': 'ReadWrite',
                        'managed_disk': {
                            'storage_account_type': disk_config.get('storage_account_type', 'Premium_LRS')
                        },
                        'name': f'{vm_name}-osdisk',
                        'create_option': DiskCreateOption.from_image,
                        'disk_size_gb': disk_config.get('os_disk_size_gb', 30)
                    }
                },
                'network_profile': {
                    'network_interfaces': [{'id': nic_id}]
                }
            }
            self._add_tags(vm_params)
            
            creation_result = self.compute_client.virtual_machines.begin_create_or_update(
                resource_group_name, vm_name, vm_params
            )
            
            vm_result = creation_result.result()
            self.logger.info(f"✓ Máquina virtual creada: {vm_result.name}")
            return vm_result
            
        except AzureError as e:
            self.logger.error(f"Error al crear máquina virtual: {e}")
            raise
    
    def get_vm_info(self, resource_group_name: str, vm_name: str) -> Dict[str, str]:
        """Obtener información de la VM creada"""
        try:
            vm = self.compute_client.virtual_machines.get(resource_group_name, vm_name)
            
            # Obtener IP pública
            network_config = self.config.get('network', {})
            public_ip_name = network_config.get('public_ip_name')
            
            public_ip_address = "No asignada"
            if public_ip_name:
                try:
                    public_ip = self.network_client.public_ip_addresses.get(
                        resource_group_name, public_ip_name
                    )
                    public_ip_address = public_ip.ip_address or "Pendiente"
                except:
                    pass
            
            return {
                'vm_name': vm.name,
                'vm_id': vm.vm_id,
                'location': vm.location,
                'vm_size': vm.hardware_profile.vm_size,
                'provisioning_state': vm.provisioning_state,
                'public_ip': public_ip_address,
                'admin_username': self.config.get('admin_username')
            }
            
        except Exception as e:
            self.logger.error(f"Error al obtener información de la VM: {e}")
            return {}
    
    def create_complete_vm(self) -> Optional[Any]:
        """Crear una VM completa con todos los recursos necesarios"""
        try:
            vm_name = self.config.get('vm_name')
            resource_group = self.config.get('resource_group')
            location = self.config.get('location')
            admin_username = self.config.get('admin_username')
            admin_password = self.config.get('admin_password')
            
            network_config = self.config.get('network', {})
            
            self.logger.info("=== Iniciando creación de infraestructura Azure ===")
            
            # Crear grupo de recursos
            self.create_resource_group(resource_group, location)
            
            # Crear red virtual
            self.create_virtual_network(
                resource_group, 
                network_config.get('vnet_name'), 
                location
            )
            
            # Crear subred
            subnet = self.create_subnet(
                resource_group, 
                network_config.get('vnet_name'), 
                network_config.get('subnet_name')
            )
            
            # Crear IP pública
            public_ip = self.create_public_ip(
                resource_group, 
                network_config.get('public_ip_name'), 
                location
            )
            
            # Crear grupo de seguridad
            nsg = self.create_network_security_group(
                resource_group, 
                network_config.get('nsg_name'), 
                location
            )
            
            # Crear interfaz de red
            nic = self.create_network_interface(
                resource_group,
                network_config.get('nic_name'),
                location,
                subnet.id,
                public_ip.id,
                nsg.id
            )
            
            # Crear máquina virtual
            vm = self.create_virtual_machine(
                resource_group, vm_name, location,
                nic.id, admin_username, admin_password
            )
            
            # Obtener información final
            vm_info = self.get_vm_info(resource_group, vm_name)
            
            self.logger.info("=== Creación completada exitosamente ===")
            self.logger.info(f"VM Name: {vm_info.get('vm_name')}")
            self.logger.info(f"VM ID: {vm_info.get('vm_id')}")
            self.logger.info(f"Location: {vm_info.get('location')}")
            self.logger.info(f"Size: {vm_info.get('vm_size')}")
            self.logger.info(f"Public IP: {vm_info.get('public_ip')}")
            self.logger.info(f"Admin User: {vm_info.get('admin_username')}")
            
            return vm
            
        except Exception as e:
            self.logger.error(f"Error en la creación de la máquina virtual: {str(e)}")
            return None


def parse_arguments() -> argparse.Namespace:
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Azure VM Creator - Herramienta profesional para crear VMs en Azure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s --vm-name mi-servidor --location "West Europe"
  %(prog)s --config config.json --log-level DEBUG
  %(prog)s --vm-name web-server --vm-size Standard_D2s_v3 --admin-user webapp
        """
    )
    
    parser.add_argument('--version', action='version', version='Azure VM Creator 2.0.0')
    
    # Configuración básica
    parser.add_argument('--config', '-c', 
                       help='Archivo de configuración JSON')
    parser.add_argument('--subscription-id', 
                       help='Azure Subscription ID (también puede usar AZURE_SUBSCRIPTION_ID)')
    
    # Configuración de VM
    parser.add_argument('--vm-name', 
                       help='Nombre de la máquina virtual')
    parser.add_argument('--resource-group', 
                       help='Nombre del grupo de recursos')
    parser.add_argument('--location', 
                       help='Ubicación de Azure (ej: East US, West Europe)')
    parser.add_argument('--vm-size', 
                       help='Tamaño de la VM (ej: Standard_B2s, Standard_D2s_v3)')
    parser.add_argument('--admin-user', 
                       help='Usuario administrador')
    parser.add_argument('--admin-password', 
                       help='Contraseña del administrador (se solicitará si no se proporciona)')
    
    # Configuración de logging
    parser.add_argument('--log-level', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='Nivel de logging (default: INFO)')
    
    # Opciones adicionales
    parser.add_argument('--dry-run', action='store_true',
                       help='Mostrar configuración sin crear recursos')
    parser.add_argument('--generate-config', 
                       help='Generar archivo de configuración de ejemplo')
    
    return parser.parse_args()


def generate_config_file(filename: str) -> None:
    """Generar archivo de configuración de ejemplo"""
    config = VMConfig()
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config.config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Archivo de configuración generado: {filename}")
    print(f"  Edita este archivo para personalizar tu configuración antes de ejecutar el script.")


def print_banner():
    """Mostrar banner profesional"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                    🚀 AZURE VM CREATOR v2.0.0 🚀                     ║
║                                                                      ║
║        Herramienta para crear VMs en Azure                           ║
║        Desarrollado por: Jennifer                                    ║
║        Fecha: 6 de junio de 2025                                     ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_menu() -> int:
    """Mostrar menú principal y obtener selección del usuario"""
    menu_options = """
┌─────────────────── MENÚ PRINCIPAL ───────────────────┐
│                                                      │
│  1. 🆕 Crear nueva máquina virtual                   │
│  2. ⚙️  Crear VM con configuración personalizada     │
│  3. 📄 Generar archivo de configuración              │
│  4. 🔍 Vista previa de configuración (dry-run)       │
│  5. 📚 Mostrar ejemplos de uso                       │
│  6. ❓ Ayuda y documentación                         │
│  7. 🚪 Salir                                         │
│                                                      │
└──────────────────────────────────────────────────────┘
    """
    
    print(menu_options)
    
    while True:
        try:
            choice = int(input("🔸 Seleccione una opción (1-7): "))
            if 1 <= choice <= 7:
                return choice
            else:
                print("❌ Por favor, seleccione un número entre 1 y 7.")
        except ValueError:
            print("❌ Por favor, ingrese un número válido.")


def interactive_vm_creation() -> Dict[str, Any]:
    """Creación interactiva de VM con validaciones"""
    print("\n" + "="*60)
    print("🔧 CONFIGURACIÓN INTERACTIVA DE MÁQUINA VIRTUAL")
    print("="*60)
    
    config = {}
    
    # Nombre de la VM
    while True:
        vm_name = input("\n📝 Nombre de la VM (ej: mi-servidor-web): ").strip()
        if vm_name and len(vm_name) <= 64 and vm_name.replace('-', '').replace('_', '').isalnum():
            config['vm_name'] = vm_name
            break
        print("❌ Nombre inválido. Use 1-64 caracteres alfanuméricos, guiones o guiones bajos.")
    
    # Grupo de recursos
    rg_name = input("\n📦 Grupo de recursos (Enter para usar 'rg-{vm_name}'): ").strip()
    config['resource_group'] = rg_name if rg_name else f"rg-{vm_name}"
    
    # Ubicación
    locations = [
        "East US", "West US", "West Europe", "North Europe",
        "Southeast Asia", "East Asia", "Brazil South", "Australia East"
    ]
    print(f"\n🌍 Ubicaciones disponibles:")
    for i, loc in enumerate(locations, 1):
        print(f"   {i}. {loc}")
    
    while True:
        try:
            loc_choice = int(input("\n🔸 Seleccione ubicación (1-8, Enter para East US): ") or "1")
            if 1 <= loc_choice <= len(locations):
                config['location'] = locations[loc_choice - 1]
                break
        except ValueError:
            pass
        print("❌ Selección inválida.")
    
    # Tamaño de VM
    vm_sizes = [
        ("Standard_B1s", "1 vCPU, 1GB RAM - Básico"),
        ("Standard_B2s", "2 vCPU, 4GB RAM - Estándar"),
        ("Standard_D2s_v3", "2 vCPU, 8GB RAM - Propósito general"),
        ("Standard_D4s_v3", "4 vCPU, 16GB RAM - Alto rendimiento")
    ]
    
    print(f"\n💻 Tamaños de VM disponibles:")
    for i, (size, desc) in enumerate(vm_sizes, 1):
        print(f"   {i}. {size} - {desc}")
    
    while True:
        try:
            size_choice = int(input("\n🔸 Seleccione tamaño (1-4, Enter para Standard_B2s): ") or "2")
            if 1 <= size_choice <= len(vm_sizes):
                config['vm_size'] = vm_sizes[size_choice - 1][0]
                break
        except ValueError:
            pass
        print("❌ Selección inválida.")
    
    # Usuario administrador
    admin_user = input(f"\n👤 Usuario administrador (Enter para 'azureuser'): ").strip()
    config['admin_username'] = admin_user if admin_user else 'azureuser'
    
    # Contraseña
    while True:
        password = getpass.getpass("\n🔐 Contraseña del administrador: ")
        if len(password) >= 8:
            config['admin_password'] = password
            break
        print("❌ La contraseña debe tener al menos 8 caracteres.")
    
    return config


def show_examples():
    """Mostrar ejemplos de uso del script"""
    examples = """
┌─────────────────── EJEMPLOS DE USO ──────────────────┐
│                                                      │
│ 📋 Uso básico desde línea de comandos:               │
│                                                      │
│   python create_vm.py --vm-name servidor-web \\      │
│                      --location "West Europe"        │
│                                                      │
│ 📋 Con configuración personalizada:                  │
│                                                      │
│   python create_vm.py --config mi-config.json \\     │
│                      --log-level DEBUG               │
│                                                      │
│ 📋 Vista previa sin crear recursos:                  │
│                                                      │
│   python create_vm.py --dry-run \\                   │
│                      --vm-name test-vm               │
│                                                      │
│ 📋 Generar configuración de ejemplo:                 │
│                                                      │
│   python create_vm.py --generate-config config.json │
│                                                      │
└──────────────────────────────────────────────────────┘
    """
    print(examples)


def show_help():
    """Mostrar ayuda y documentación"""
    help_text = """
┌─────────────────── AYUDA Y DOCUMENTACIÓN ────────────────────┐
│                                                              │
│ 🔧 CONFIGURACIÓN INICIAL:                                    │
│                                                              │
│   1. Instalar dependencias:                                  │
│      pip install -r requirements.txt                         │
│                                                              │
│   2. Autenticarse en Azure:                                  │
│      az login                                                │
│                                                              │
│   3. Configurar Subscription ID:                             │
│      export AZURE_SUBSCRIPTION_ID="tu-subscription-id"       │
│                                                              │
│ 📋 CARACTERÍSTICAS:                                          │
│                                                              │
│   • Creación automatizada de todos los recursos              │
│   • Configuración de seguridad por defecto                   │
│   • Logging detallado y manejo de errores                    │
│   • Soporte para configuración externa (JSON)                │
│   • Modo dry-run para vista previa                           │
│   • Tags automáticos para organización                       │
│                                                              │
│ 🔗 RECURSOS CREADOS:                                         │
│                                                              │
│   • Grupo de recursos                                        │
│   • Red virtual y subred                                     │
│   • IP pública                                               │
│   • Grupo de seguridad de red                                │
│   • Interfaz de red                                          │
│   • Máquina virtual                                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
    """
    print(help_text)


def interactive_menu_mode():
    """Modo de menú interactivo"""
    print_banner()
    
    while True:
        choice = show_menu()
        
        if choice == 1:
            # Crear nueva VM con configuración por defecto
            print("\n🚀 Iniciando creación de VM con configuración por defecto...")
            return 'create_default'
            
        elif choice == 2:
            # Crear VM con configuración personalizada
            print("\n🔧 Iniciando configuración personalizada...")
            custom_config = interactive_vm_creation()
            return 'create_custom', custom_config
            
        elif choice == 3:
            # Generar archivo de configuración
            filename = input("\n📄 Nombre del archivo de configuración (config.json): ").strip()
            if not filename:
                filename = "config.json"
            generate_config_file(filename)
            input("\n✅ Presione Enter para continuar...")
            
        elif choice == 4:
            # Vista previa (dry-run)
            print("\n🔍 Modo vista previa activado...")
            return 'dry_run'
            
        elif choice == 5:
            # Mostrar ejemplos
            show_examples()
            input("\n📚 Presione Enter para continuar...")
            
        elif choice == 6:
            # Mostrar ayuda
            show_help()
            input("\n❓ Presione Enter para continuar...")
            
        elif choice == 7:
            # Salir
            print("\n👋 ¡Gracias por usar Azure VM Creator!")
            sys.exit(0)


def main():
    """Función principal"""
    args = parse_arguments()
    
    # Si no hay argumentos, mostrar menú interactivo
    if len(sys.argv) == 1:
        menu_result = interactive_menu_mode()
        
        if menu_result == 'create_default':
            # Usar configuración por defecto
            config = VMConfig()
            # Solicitar contraseña
            password = getpass.getpass("🔐 Ingrese la contraseña del administrador: ")
            if not password:
                print("❌ Contraseña requerida")
                sys.exit(1)
            config.config['admin_password'] = password
            
        elif isinstance(menu_result, tuple) and menu_result[0] == 'create_custom':
            # Usar configuración personalizada del menú
            config = VMConfig()
            config.config.update(menu_result[1])
            
        elif menu_result == 'dry_run':
            # Modo dry-run con configuración por defecto
            config = VMConfig()
            logger = setup_logging('INFO')
            logger.info("=== MODO DRY-RUN - Configuración por defecto ===")
            print(json.dumps(config.config, indent=2, ensure_ascii=False))
            return
            
    else:
        # Generar configuración si se solicita
        if args.generate_config:
            generate_config_file(args.generate_config)
            return
        
        # Cargar configuración
        config = VMConfig(args.config)
        
        # Aplicar argumentos de línea de comandos
        if args.vm_name:
            config.config['vm_name'] = args.vm_name
        if args.resource_group:
            config.config['resource_group'] = args.resource_group
        if args.location:
            config.config['location'] = args.location
        if args.vm_size:
            config.config['vm_size'] = args.vm_size
        if args.admin_user:
            config.config['admin_username'] = args.admin_user
        
        # Solicitar contraseña si no se proporcionó
        if args.admin_password:
            config.config['admin_password'] = args.admin_password
        elif not config.get('admin_password'):
            password = getpass.getpass("🔐 Ingrese la contraseña del administrador: ")
            if not password:
                print("❌ Contraseña requerida")
                sys.exit(1)
            config.config['admin_password'] = password
        
        # Modo dry-run
        if args.dry_run:
            logger = setup_logging(args.log_level)
            logger.info("=== MODO DRY-RUN - Configuración a usar ===")
            print(json.dumps(config.config, indent=2, ensure_ascii=False))
            return
    
    # Configurar logging
    log_level = getattr(args, 'log_level', 'INFO')
    logger = setup_logging(log_level)
    logger.info("=== Azure VM Creator v2.0.0 ===")
    
    try:
        # Validar configuración
        if not config.validate():
            logger.error("❌ Configuración inválida")
            sys.exit(1)
        
        # Obtener subscription ID
        subscription_id = getattr(args, 'subscription_id', None) or os.environ.get('AZURE_SUBSCRIPTION_ID')
        if not subscription_id:
            print("\n❌ Azure Subscription ID requerido")
            print("💡 Opciones:")
            print("   1. Use --subscription-id en línea de comandos")
            print("   2. Configure: export AZURE_SUBSCRIPTION_ID='tu-subscription-id'")
            print("   3. Use: az account show --query id --output tsv")
            sys.exit(1)
        
        logger.info(f"📋 Subscription ID: {subscription_id}")
        
        # Mostrar resumen de configuración
        print(f"\n📋 RESUMEN DE CONFIGURACIÓN:")
        print(f"   🏷️  VM Name: {config.get('vm_name')}")
        print(f"   📦 Resource Group: {config.get('resource_group')}")
        print(f"   🌍 Location: {config.get('location')}")
        print(f"   💻 VM Size: {config.get('vm_size')}")
        print(f"   👤 Admin User: {config.get('admin_username')}")
        
        # Confirmación para proceder
        if len(sys.argv) == 1:  # Solo en modo interactivo
            confirm = input(f"\n🤔 ¿Proceder con la creación? (s/N): ").strip().lower()
            if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
                print("⏹️  Operación cancelada por el usuario.")
                sys.exit(0)
        
        # Crear instancia del creador de VMs
        vm_creator = AzureVMCreator(subscription_id, config)
        
        # Crear la máquina virtual
        print(f"\n🚀 Iniciando creación de infraestructura Azure...")
        result = vm_creator.create_complete_vm()
        
        if result:
            print(f"\n🎉 ¡Máquina virtual creada exitosamente!")
            print(f"📝 Revise los logs para obtener detalles completos.")
            logger.info("✅ Proceso completado exitosamente")
        else:
            print(f"\n❌ Error en la creación de la máquina virtual.")
            logger.error("❌ El proceso falló")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏸️  Proceso interrumpido por el usuario")
        logger.warning("Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
