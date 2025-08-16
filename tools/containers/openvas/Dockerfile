# OpenVAS Vulnerability Scanner Container
# Pentest-USB Toolkit - Docker Configuration
# Version: 1.0.0

FROM ubuntu:22.04

LABEL maintainer="Pentest-USB Team"
LABEL description="OpenVAS Vulnerability Scanner for Pentest-USB Toolkit"
LABEL version="1.0.0"

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg2 \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    lsb-release \
    sudo \
    supervisor \
    rsync \
    nmap \
    nikto \
    dirb \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Add GVM (Greenbone Vulnerability Management) repository
RUN curl -fsSL https://www.greenbone.net/GBCommunitySigningKey.asc | gpg --dearmor -o /etc/apt/keyrings/greenbone.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/greenbone.gpg] https://packages.greenbone.net/community/22.04 stable main" | tee /etc/apt/sources.list.d/greenbone.list

# Update package list and install GVM
RUN apt-get update && apt-get install -y \
    gvm \
    greenbone-vulnerability-manager \
    greenbone-security-assistant \
    greenbone-ospd-openvas \
    greenbone-feed-sync \
    && rm -rf /var/lib/apt/lists/*

# Alternative: Build from source (commented out - use if repository is unavailable)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     cmake \
#     pkg-config \
#     libglib2.0-dev \
#     libgpgme11-dev \
#     libgnutls28-dev \
#     uuid-dev \
#     libssh-gcrypt-dev \
#     libldap2-dev \
#     libhiredis-dev \
#     libxml2-dev \
#     libpcap-dev \
#     libnet1-dev \
#     libpaho-mqtt-dev \
#     python3-pip \
#     && rm -rf /var/lib/apt/lists/*

# Create GVM user and group
RUN adduser --system --no-create-home --disabled-password --shell /bin/bash gvm && \
    addgroup --system gvm && \
    usermod -aG gvm gvm

# Create necessary directories
RUN mkdir -p \
    /var/lib/gvm \
    /var/log/gvm \
    /var/run/gvm \
    /opt/gvm \
    /etc/gvm \
    /var/lib/openvas/plugins \
    /etc/supervisor/conf.d

# Set ownership and permissions
RUN chown -R gvm:gvm /var/lib/gvm /var/log/gvm /var/run/gvm /opt/gvm && \
    chmod 755 /var/lib/gvm /var/log/gvm /var/run/gvm

# Create GVM configuration files
RUN mkdir -p /etc/gvm && \
    cat > /etc/gvm/gvmd.conf << 'EOF'
# GVM Manager Configuration
# Pentest-USB Toolkit Integration

# Database configuration
db_host = localhost
db_port = 5432
db_name = gvmd
db_user = gvm
db_password = gvm

# Listening configuration
listen_address = 0.0.0.0
listen_port = 9390

# SSL/TLS configuration
cert_file = /var/lib/gvm/CA/servercert.pem
key_file = /var/lib/gvm/private/serverkey.pem
ca_file = /var/lib/gvm/CA/cacert.pem

# Logging
log_level = MESSAGE
log_file = /var/log/gvm/gvmd.log

# Performance settings
max_ips_per_target = 4096
max_email_attachment_size = 64
max_email_include_size = 64
EOF

RUN cat > /etc/gvm/openvas.conf << 'EOF'
# OpenVAS Scanner Configuration
# Pentest-USB Toolkit Integration

# Network settings
timeout_checks = 5
optimize_test = yes
network_scan = yes
ping_hosts = yes

# Performance settings
max_checks = 10
max_hosts = 30
be_nice = no

# Plugin settings
plugins_folder = /var/lib/openvas/plugins
include_kb = yes
kb_restore = no
kb_dont_replay_scanners = no
kb_dont_replay_info_gathering = no
kb_max_age = 864000

# Logging
log_level = 2
log_file = /var/log/gvm/openvas.log

# CGI paths
cgi_path = /cgi-bin:/scripts:/cgi-local:/htbin:/cgibin:/cgis:/cgi-win:/bin

# Safe checks
safe_checks = yes
auto_enable_dependencies = yes
EOF

# Create supervisor configuration for GVM services
RUN cat > /etc/supervisor/conf.d/gvm.conf << 'EOF'
[supervisord]
nodaemon=true
user=root

[program:gvmd]
command=/usr/sbin/gvmd --listen=0.0.0.0 --port=9390
user=gvm
autostart=true
autorestart=true
stdout_logfile=/var/log/gvm/gvmd.log
stderr_logfile=/var/log/gvm/gvmd.log

[program:openvas]
command=/usr/sbin/openvas --listen=0.0.0.0 --port=9391
user=gvm
autostart=true
autorestart=true
stdout_logfile=/var/log/gvm/openvas.log
stderr_logfile=/var/log/gvm/openvas.log

[program:gsad]
command=/usr/sbin/gsad --listen=0.0.0.0 --port=443 --mlisten=127.0.0.1 --mport=9390 --no-redirect
user=gvm
autostart=true
autorestart=true
stdout_logfile=/var/log/gvm/gsad.log
stderr_logfile=/var/log/gvm/gsad.log
EOF

# Copy setup script
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh

# Create initialization script
RUN cat > /init-gvm.sh << 'EOF'
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[+] Initializing OpenVAS/GVM${NC}"

# Switch to gvm user for initialization
sudo -u gvm bash << 'GVMEOF'

# Check if already initialized
if [ -f /var/lib/gvm/.initialized ]; then
    echo -e "${GREEN}[+] GVM already initialized${NC}"
    exit 0
fi

echo -e "${YELLOW}[*] Creating GVM certificates...${NC}"
gvm-manage-certs -a

echo -e "${YELLOW}[*] Creating GVM user...${NC}"
gvmd --create-user=admin --password=admin

echo -e "${YELLOW}[*] Setting up feeds...${NC}"
greenbone-feed-sync --type GVMD_DATA
greenbone-feed-sync --type SCAP
greenbone-feed-sync --type CERT

echo -e "${YELLOW}[*] Updating NVT feed...${NC}"
greenbone-feed-sync --type NVT

echo -e "${YELLOW}[*] Rebuilding database...${NC}"
gvmd --rebuild

# Mark as initialized
touch /var/lib/gvm/.initialized

echo -e "${GREEN}[+] GVM initialization complete${NC}"

GVMEOF
EOF

RUN chmod +x /init-gvm.sh

# Create startup script
RUN cat > /start-gvm.sh << 'EOF'
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[+] Starting OpenVAS/GVM Container${NC}"
echo -e "${GREEN}[+] Pentest-USB Toolkit Integration${NC}"

# Initialize GVM if not done
if [ ! -f /var/lib/gvm/.initialized ]; then
    echo -e "${YELLOW}[*] First time setup - this may take several minutes...${NC}"
    /init-gvm.sh
fi

# Start services with supervisor
echo -e "${YELLOW}[*] Starting GVM services...${NC}"
supervisord -c /etc/supervisor/supervisord.conf
EOF

RUN chmod +x /start-gvm.sh

# Install Python dependencies for automation
RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install \
    gvm-tools \
    python-gvm \
    requests \
    && rm -rf /var/lib/apt/lists/*

# Create automation scripts
RUN mkdir -p /opt/gvm-scripts && \
    cat > /opt/gvm-scripts/auto-scan.py << 'EOF'
#!/usr/bin/env python3
"""
OpenVAS/GVM Automated Scanning Script
Pentest-USB Toolkit Integration
"""

import sys
import time
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto-scan.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    try:
        # Connect to GVM
        connection = UnixSocketConnection('/var/run/gvm/gvmd.sock')
        transform = EtreeTransform()
        
        with Gmp(connection, transform=transform) as gmp:
            # Authenticate
            gmp.authenticate('admin', 'admin')
            
            print(f"[+] Starting scan of {target}")
            
            # Create target
            target_resp = gmp.create_target(
                name=f"Pentest-USB-{target}",
                hosts=[target]
            )
            target_id = target_resp.get('id')
            
            # Get scan config (Full and fast)
            configs = gmp.get_scan_configs()
            config_id = None
            for config in configs.xpath('config'):
                if 'Full and fast' in config.find('name').text:
                    config_id = config.get('id')
                    break
            
            if not config_id:
                print("[-] Could not find scan configuration")
                return
            
            # Create task
            task_resp = gmp.create_task(
                name=f"Pentest-USB-Scan-{target}",
                config_id=config_id,
                target_id=target_id,
                scanner_id='08b69003-5fc2-4037-a479-93b440211c73'  # Default OpenVAS scanner
            )
            task_id = task_resp.get('id')
            
            # Start task
            gmp.start_task(task_id)
            
            print("[*] Scan started, monitoring progress...")
            
            # Monitor progress
            while True:
                task_status = gmp.get_task(task_id)
                status = task_status.find('task/status').text
                progress = task_status.find('task/progress').text
                
                print(f"Status: {status}, Progress: {progress}%")
                
                if status in ['Done', 'Stopped']:
                    break
                
                time.sleep(30)
            
            print("[+] Scan completed")
            
            # Get results
            results = gmp.get_results(task_id=task_id)
            result_count = len(results.xpath('result'))
            
            print(f"[+] Found {result_count} results")
            
            # Generate report
            report_resp = gmp.create_report(
                name=f"Pentest-USB-Report-{target}",
                results=results
            )
            
            print("[+] Report generated successfully")
            
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    main()
EOF

RUN chmod +x /opt/gvm-scripts/auto-scan.py

# Set proper ownership
RUN chown -R gvm:gvm /var/lib/gvm /var/log/gvm /var/run/gvm /opt/gvm-scripts

# Expose ports
EXPOSE 443 9390 9391

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=300s --retries=3 \
    CMD curl -k -f https://localhost:443/ || exit 1

# Set working directory
WORKDIR /opt/gvm

CMD ["/start-gvm.sh"]