#!/bin/bash
# OpenVAS/GVM Setup Script
# Pentest-USB Toolkit - Docker Configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  OpenVAS/GVM Setup Script${NC}"
echo -e "${GREEN}  Pentest-USB Toolkit Integration${NC}"
echo -e "${GREEN}================================================================${NC}"

# Function to log with timestamp
log() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log "Running as root - switching to gvm user for operations"
    SUDO_PREFIX="sudo -u gvm"
else
    log "Running as non-root user"
    SUDO_PREFIX=""
fi

# Create necessary directories
log "Creating GVM directories..."
mkdir -p /var/lib/gvm/{CA,private}
mkdir -p /var/log/gvm
mkdir -p /var/run/gvm
mkdir -p /etc/gvm
mkdir -p /var/lib/openvas/plugins

# Set proper ownership
chown -R gvm:gvm /var/lib/gvm /var/log/gvm /var/run/gvm
chmod 750 /var/lib/gvm/private

# Generate certificates
log "Generating GVM certificates..."
$SUDO_PREFIX gvm-manage-certs -a

if [ $? -eq 0 ]; then
    success "Certificates generated successfully"
else
    error "Failed to generate certificates"
    exit 1
fi

# Initialize feeds
log "Initializing GVM feeds (this may take a while)..."

# Download SCAP data
log "Downloading SCAP data..."
$SUDO_PREFIX greenbone-feed-sync --type SCAP

# Download CERT data
log "Downloading CERT data..."
$SUDO_PREFIX greenbone-feed-sync --type CERT

# Download GVMD data
log "Downloading GVMD data..."
$SUDO_PREFIX greenbone-feed-sync --type GVMD_DATA

# Download NVT data
log "Downloading NVT data..."
$SUDO_PREFIX greenbone-feed-sync --type NVT

# Update database
log "Updating GVM database..."
$SUDO_PREFIX gvmd --rebuild

if [ $? -eq 0 ]; then
    success "Database updated successfully"
else
    error "Failed to update database"
    exit 1
fi

# Create admin user
log "Creating admin user..."
$SUDO_PREFIX gvmd --create-user=admin --password=admin

if [ $? -eq 0 ]; then
    success "Admin user created (username: admin, password: admin)"
else
    log "Admin user might already exist"
fi

# Get scanner UUID
log "Getting scanner information..."
SCANNER_UUID=$($SUDO_PREFIX gvmd --get-scanners | grep -E '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}' | head -1)

if [ ! -z "$SCANNER_UUID" ]; then
    success "Scanner UUID: $SCANNER_UUID"
else
    log "No scanner UUID found - creating default scanner"
    $SUDO_PREFIX gvmd --create-scanner="OpenVAS Scanner" --scanner-type="OpenVAS" --scanner-host="/var/run/ospd/ospd-openvas.sock"
fi

# Create sample scan configurations
log "Setting up scan configurations..."

# Create Pentest-USB specific scan config
cat > /tmp/pentest-usb-config.xml << 'EOF'
<create_config>
  <name>Pentest-USB Full Scan</name>
  <comment>Comprehensive scan configuration for Pentest-USB Toolkit</comment>
  <copy>daba56c8-73ec-11df-a475-002264764cea</copy>
</create_config>
EOF

$SUDO_PREFIX gvmd --create-config=/tmp/pentest-usb-config.xml 2>/dev/null || log "Custom config may already exist"

# Create automation script for Pentest-USB integration
log "Creating automation scripts..."

cat > /var/lib/gvm/pentest-usb-automation.py << 'EOF'
#!/usr/bin/env python3
"""
Pentest-USB GVM Automation Script
Provides easy integration with the Pentest-USB Toolkit
"""

import sys
import json
import time
import argparse
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform

class PentestUSBGVM:
    def __init__(self):
        self.connection = UnixSocketConnection('/var/run/gvm/gvmd.sock')
        self.transform = EtreeTransform()
        
    def create_target(self, name, hosts):
        """Create a new target"""
        with Gmp(self.connection, transform=self.transform) as gmp:
            gmp.authenticate('admin', 'admin')
            
            response = gmp.create_target(name=name, hosts=hosts)
            return response.get('id')
    
    def start_scan(self, target_id, config_name="Full and fast"):
        """Start a scan on a target"""
        with Gmp(self.connection, transform=self.transform) as gmp:
            gmp.authenticate('admin', 'admin')
            
            # Get config ID
            configs = gmp.get_scan_configs()
            config_id = None
            
            for config in configs.xpath('config'):
                if config_name in config.find('name').text:
                    config_id = config.get('id')
                    break
            
            if not config_id:
                raise Exception(f"Config '{config_name}' not found")
            
            # Create task
            task_resp = gmp.create_task(
                name=f"Pentest-USB-Task-{int(time.time())}",
                config_id=config_id,
                target_id=target_id,
                scanner_id='08b69003-5fc2-4037-a479-93b440211c73'
            )
            
            task_id = task_resp.get('id')
            
            # Start task
            gmp.start_task(task_id)
            
            return task_id
    
    def get_scan_status(self, task_id):
        """Get scan status and progress"""
        with Gmp(self.connection, transform=self.transform) as gmp:
            gmp.authenticate('admin', 'admin')
            
            task = gmp.get_task(task_id)
            status = task.find('task/status').text
            progress = task.find('task/progress').text
            
            return {'status': status, 'progress': progress}
    
    def get_results(self, task_id):
        """Get scan results"""
        with Gmp(self.connection, transform=self.transform) as gmp:
            gmp.authenticate('admin', 'admin')
            
            results = gmp.get_results(task_id=task_id)
            
            vulnerabilities = []
            for result in results.xpath('result'):
                vuln = {
                    'name': result.find('name').text if result.find('name') is not None else 'Unknown',
                    'severity': result.find('severity').text if result.find('severity') is not None else '0',
                    'host': result.find('host').text if result.find('host') is not None else 'Unknown',
                    'port': result.find('port').text if result.find('port') is not None else 'Unknown',
                    'description': result.find('description').text if result.find('description') is not None else 'No description'
                }
                vulnerabilities.append(vuln)
            
            return vulnerabilities

def main():
    parser = argparse.ArgumentParser(description='Pentest-USB GVM Automation')
    parser.add_argument('command', choices=['scan', 'status', 'results'])
    parser.add_argument('--target', required=False, help='Target host or IP')
    parser.add_argument('--task-id', required=False, help='Task ID for status/results')
    parser.add_argument('--config', default='Full and fast', help='Scan configuration')
    
    args = parser.parse_args()
    
    gvm = PentestUSBGVM()
    
    try:
        if args.command == 'scan':
            if not args.target:
                print("Error: --target required for scan command")
                sys.exit(1)
            
            print(f"Creating target for {args.target}...")
            target_id = gvm.create_target(f"Pentest-USB-{args.target}", [args.target])
            
            print(f"Starting scan with config '{args.config}'...")
            task_id = gvm.start_scan(target_id, args.config)
            
            print(f"Scan started. Task ID: {task_id}")
            print(f"Monitor with: python3 {sys.argv[0]} status --task-id {task_id}")
            
        elif args.command == 'status':
            if not args.task_id:
                print("Error: --task-id required for status command")
                sys.exit(1)
            
            status = gvm.get_scan_status(args.task_id)
            print(f"Status: {status['status']}")
            print(f"Progress: {status['progress']}%")
            
        elif args.command == 'results':
            if not args.task_id:
                print("Error: --task-id required for results command")
                sys.exit(1)
            
            results = gvm.get_results(args.task_id)
            
            print(f"Found {len(results)} vulnerabilities:")
            for i, vuln in enumerate(results, 1):
                print(f"\n{i}. {vuln['name']}")
                print(f"   Severity: {vuln['severity']}")
                print(f"   Host: {vuln['host']}:{vuln['port']}")
                print(f"   Description: {vuln['description'][:100]}...")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x /var/lib/gvm/pentest-usb-automation.py
chown gvm:gvm /var/lib/gvm/pentest-usb-automation.py

# Create systemd service files (if systemd is available)
if command -v systemctl &> /dev/null; then
    log "Creating systemd service files..."
    
    cat > /etc/systemd/system/gvmd.service << 'EOF'
[Unit]
Description=Greenbone Vulnerability Manager daemon (gvmd)
After=network.target networking.service postgresql.service ospd-openvas.service
Wants=postgresql.service ospd-openvas.service
Documentation=man:gvmd(8)
ConditionKernelCommandLine=!recovery

[Service]
Type=notify
User=gvm
Group=gvm
PIDFile=/var/run/gvm/gvmd.pid
WorkingDirectory=/var/lib/gvm
ExecStart=/usr/sbin/gvmd --listen=127.0.0.1 --port=9390
Restart=always
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
Alias=greenbone-vulnerability-manager.service
EOF

    cat > /etc/systemd/system/gsad.service << 'EOF'
[Unit]
Description=Greenbone Security Assistant daemon (gsad)
Documentation=man:gsad(8)
After=network.target gvmd.service
Wants=gvmd.service

[Service]
Type=simple
User=gvm
Group=gvm
RuntimeDirectory=gsad
PIDFile=/var/run/gsad/gsad.pid
ExecStart=/usr/sbin/gsad --listen=0.0.0.0 --port=443 --http-only --no-redirect
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
Alias=greenbone-security-assistant.service
EOF
fi

# Mark setup as complete
touch /var/lib/gvm/.setup_complete

success "OpenVAS/GVM setup completed successfully!"

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Setup Summary${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${YELLOW}  Web Interface:     https://localhost:443${NC}"
echo -e "${YELLOW}  Username:          admin${NC}"
echo -e "${YELLOW}  Password:          admin${NC}"
echo -e "${YELLOW}  Management Port:   9390${NC}"
echo -e "${YELLOW}  Scanner Port:      9391${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${YELLOW}  Next Steps:${NC}"
echo -e "  1. Start the container with docker run"
echo -e "  2. Access web interface at https://localhost:443"
echo -e "  3. Login with admin/admin credentials"
echo -e "  4. Change default password"
echo -e "  5. Use automation script: /var/lib/gvm/pentest-usb-automation.py"
echo -e "${GREEN}================================================================${NC}"

log "Setup script completed successfully"