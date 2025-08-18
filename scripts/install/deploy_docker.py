#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Docker Deployment Script
# =============================================================================
# Description: Automated Docker deployment and orchestration script
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import time
import yaml
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/docker_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DockerDeploymentManager:
    """Manages Docker deployment for LeZelote-Toolkit"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docker_dir = self.project_root / "runtime" / "docker"
        self.tools_dir = self.project_root / "tools" / "containers"
        self.config_file = self.docker_dir / "containers.json"
        self.compose_file = self.docker_dir / "docker-compose.yml"
        
    def check_docker_availability(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Docker found: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            subprocess.run(['docker', 'info'], 
                          capture_output=True, text=True, check=True)
            logger.info("Docker daemon is running")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Docker not available: {e}")
            return False
    
    def check_docker_compose_availability(self) -> bool:
        """Check if Docker Compose is installed"""
        try:
            # Try new docker compose command first
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Docker Compose found: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            try:
                # Try legacy docker-compose command
                result = subprocess.run(['docker-compose', '--version'], 
                                      capture_output=True, text=True, check=True)
                logger.info(f"Docker Compose (legacy) found: {result.stdout.strip()}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"Docker Compose not available: {e}")
                return False
    
    def load_container_config(self) -> Dict:
        """Load container configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded container configuration with {len(config.get('services', {}))} services")
            return config
        except FileNotFoundError:
            logger.error(f"Container configuration not found: {self.config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in container configuration: {e}")
            raise
    
    def generate_docker_compose(self, profile: str = "standard") -> None:
        """Generate docker-compose.yml from configuration"""
        logger.info(f"Generating docker-compose.yml for profile: {profile}")
        
        config = self.load_container_config()
        services = config.get('services', {})
        profiles_config = config.get('profiles', {})
        
        if profile not in profiles_config:
            logger.error(f"Profile '{profile}' not found in configuration")
            raise ValueError(f"Invalid profile: {profile}")
        
        profile_services = profiles_config[profile].get('services', [])
        
        compose_config = {
            'version': '3.8',
            'services': {},
            'networks': {
                'lezelote-network': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [{'subnet': '172.20.0.0/16'}]
                    }
                }
            },
            'volumes': {
                'lezelote-data': {'driver': 'local'},
                'lezelote-logs': {'driver': 'local'},
                'lezelote-outputs': {'driver': 'local'}
            }
        }
        
        # Add selected services to compose configuration
        for service_name in profile_services:
            if service_name in services:
                service_config = services[service_name].copy()
                
                # Process environment variables
                if 'environment' in service_config:
                    env_vars = {}
                    for key, value in service_config['environment'].items():
                        # Replace placeholders
                        if isinstance(value, str):
                            value = value.replace('${PROJECT_ROOT}', str(self.project_root))
                        env_vars[key] = value
                    service_config['environment'] = env_vars
                
                # Process volumes
                if 'volumes' in service_config:
                    volumes = []
                    for volume in service_config['volumes']:
                        if isinstance(volume, str) and '${PROJECT_ROOT}' in volume:
                            volume = volume.replace('${PROJECT_ROOT}', str(self.project_root))
                        volumes.append(volume)
                    service_config['volumes'] = volumes
                
                # Add to networks
                service_config['networks'] = ['lezelote-network']
                
                compose_config['services'][service_name] = service_config
                logger.info(f"Added service: {service_name}")
        
        # Write docker-compose.yml
        with open(self.compose_file, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Generated docker-compose.yml with {len(compose_config['services'])} services")
    
    def pull_images(self, services: Optional[List[str]] = None) -> bool:
        """Pull Docker images for specified services"""
        logger.info("Pulling Docker images...")
        
        try:
            cmd = ['docker', 'compose', '-f', str(self.compose_file), 'pull']
            if services:
                cmd.extend(services)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Successfully pulled all images")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull images: {e.stderr}")
            return False
    
    def build_custom_images(self, services: Optional[List[str]] = None) -> bool:
        """Build custom Docker images"""
        logger.info("Building custom Docker images...")
        
        try:
            cmd = ['docker', 'compose', '-f', str(self.compose_file), 'build']
            if services:
                cmd.extend(services)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Successfully built custom images")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build images: {e.stderr}")
            return False
    
    def start_services(self, services: Optional[List[str]] = None, 
                      detached: bool = True) -> bool:
        """Start Docker services"""
        logger.info("Starting Docker services...")
        
        try:
            cmd = ['docker', 'compose', '-f', str(self.compose_file), 'up']
            if detached:
                cmd.append('-d')
            if services:
                cmd.extend(services)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Successfully started services")
            
            # Wait for services to be ready
            self.wait_for_services_health()
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start services: {e.stderr}")
            return False
    
    def stop_services(self, services: Optional[List[str]] = None) -> bool:
        """Stop Docker services"""
        logger.info("Stopping Docker services...")
        
        try:
            cmd = ['docker', 'compose', '-f', str(self.compose_file), 'down']
            if services:
                # For selective stopping, use stop command
                cmd = ['docker', 'compose', '-f', str(self.compose_file), 'stop']
                cmd.extend(services)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Successfully stopped services")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop services: {e.stderr}")
            return False
    
    def restart_services(self, services: Optional[List[str]] = None) -> bool:
        """Restart Docker services"""
        logger.info("Restarting Docker services...")
        
        try:
            cmd = ['docker', 'compose', '-f', str(self.compose_file), 'restart']
            if services:
                cmd.extend(services)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Successfully restarted services")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart services: {e.stderr}")
            return False
    
    def get_services_status(self) -> Dict[str, str]:
        """Get status of all services"""
        try:
            result = subprocess.run(['docker', 'compose', '-f', str(self.compose_file), 'ps'],
                                  capture_output=True, text=True, check=True)
            
            # Parse output to get service status
            lines = result.stdout.strip().split('\n')
            services_status = {}
            
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        service_name = parts[0].split('_')[-1]  # Extract service name
                        status = parts[1] if len(parts) > 1 else "unknown"
                        services_status[service_name] = status
            
            return services_status
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get services status: {e}")
            return {}
    
    def wait_for_services_health(self, timeout: int = 60) -> bool:
        """Wait for services to become healthy"""
        logger.info(f"Waiting for services to become healthy (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_services_status()
            
            if not status:
                time.sleep(5)
                continue
                
            healthy_services = sum(1 for s in status.values() if 'up' in s.lower())
            total_services = len(status)
            
            if healthy_services == total_services and total_services > 0:
                logger.info("All services are healthy")
                return True
            
            logger.info(f"Services health: {healthy_services}/{total_services} healthy")
            time.sleep(5)
        
        logger.error("Timeout waiting for services to become healthy")
        return False
    
    def show_services_logs(self, services: Optional[List[str]] = None, 
                          follow: bool = False, lines: int = 50) -> None:
        """Show logs for services"""
        try:
            cmd = ['docker', 'compose', '-f', str(self.compose_file), 'logs']
            if follow:
                cmd.append('-f')
            cmd.extend(['--tail', str(lines)])
            if services:
                cmd.extend(services)
            
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to show logs: {e}")
    
    def cleanup_deployment(self, remove_volumes: bool = False) -> bool:
        """Clean up Docker deployment"""
        logger.info("Cleaning up Docker deployment...")
        
        try:
            cmd = ['docker', 'compose', '-f', str(self.compose_file), 'down']
            if remove_volumes:
                cmd.append('-v')
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Successfully cleaned up deployment")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to cleanup deployment: {e.stderr}")
            return False
    
    def export_services_info(self, output_file: str) -> bool:
        """Export services information to JSON file"""
        try:
            config = self.load_container_config()
            status = self.get_services_status()
            
            services_info = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'services': config.get('services', {}),
                'status': status,
                'profiles': config.get('profiles', {})
            }
            
            with open(output_file, 'w') as f:
                json.dump(services_info, f, indent=2)
            
            logger.info(f"Services information exported to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export services info: {e}")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Docker Deployment Manager")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    parser.add_argument('--profile', default='standard',
                       choices=['minimal', 'standard', 'comprehensive', 'enterprise'],
                       help='Deployment profile')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy services')
    deploy_parser.add_argument('--build', action='store_true', help='Build images before deployment')
    deploy_parser.add_argument('--services', nargs='*', help='Specific services to deploy')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start services')
    start_parser.add_argument('--services', nargs='*', help='Specific services to start')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop services')
    stop_parser.add_argument('--services', nargs='*', help='Specific services to stop')
    
    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart services')
    restart_parser.add_argument('--services', nargs='*', help='Specific services to restart')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show services status')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show services logs')
    logs_parser.add_argument('--follow', '-f', action='store_true', help='Follow log output')
    logs_parser.add_argument('--lines', type=int, default=50, help='Number of lines to show')
    logs_parser.add_argument('--services', nargs='*', help='Specific services to show logs for')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up deployment')
    cleanup_parser.add_argument('--remove-volumes', action='store_true', help='Remove volumes')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export services information')
    export_parser.add_argument('--output', default='services_info.json', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create deployment manager
    manager = DockerDeploymentManager(args.project_root)
    
    # Check Docker availability
    if not manager.check_docker_availability():
        logger.error("Docker is not available. Please install Docker and try again.")
        sys.exit(1)
    
    if not manager.check_docker_compose_availability():
        logger.error("Docker Compose is not available. Please install Docker Compose and try again.")
        sys.exit(1)
    
    # Execute commands
    try:
        if args.command == 'deploy':
            manager.generate_docker_compose(args.profile)
            
            if args.build:
                if not manager.build_custom_images(args.services):
                    sys.exit(1)
            else:
                if not manager.pull_images(args.services):
                    sys.exit(1)
            
            if not manager.start_services(args.services):
                sys.exit(1)
            
            logger.info("Deployment completed successfully!")
            
        elif args.command == 'start':
            if not manager.start_services(args.services):
                sys.exit(1)
                
        elif args.command == 'stop':
            if not manager.stop_services(args.services):
                sys.exit(1)
                
        elif args.command == 'restart':
            if not manager.restart_services(args.services):
                sys.exit(1)
                
        elif args.command == 'status':
            status = manager.get_services_status()
            if status:
                print("\nServices Status:")
                print("-" * 50)
                for service, status_text in status.items():
                    print(f"{service:<20} : {status_text}")
            else:
                print("No services found or not running")
                
        elif args.command == 'logs':
            manager.show_services_logs(args.services, args.follow, args.lines)
            
        elif args.command == 'cleanup':
            if not manager.cleanup_deployment(args.remove_volumes):
                sys.exit(1)
                
        elif args.command == 'export':
            if not manager.export_services_info(args.output):
                sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()