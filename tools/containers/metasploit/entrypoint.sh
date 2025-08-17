#!/bin/bash
# Metasploit Framework Entrypoint Script
# Pentest-USB Toolkit - Docker Configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[+] Starting Metasploit Framework Container${NC}"
echo -e "${GREEN}[+] Pentest-USB Toolkit - Version 1.0.0${NC}"

# Start PostgreSQL service
echo -e "${YELLOW}[*] Starting PostgreSQL database...${NC}"
sudo service postgresql start

# Wait for PostgreSQL to be ready
sleep 5

# Initialize Metasploit database if not already done
if [ ! -f /home/msf/.msf4/database_initialized ]; then
    echo -e "${YELLOW}[*] Initializing Metasploit database...${NC}"
    msfdb init
    
    # Mark database as initialized
    touch /home/msf/.msf4/database_initialized
    echo -e "${GREEN}[+] Database initialization complete${NC}"
else
    echo -e "${GREEN}[+] Database already initialized${NC}"
fi

# Start Metasploit RPC daemon if requested
if [ "$START_RPC" = "true" ]; then
    echo -e "${YELLOW}[*] Starting Metasploit RPC daemon...${NC}"
    msfrpcd -P "$MSF_RPC_PASS" -S -a 0.0.0.0 -p 55553 &
    echo -e "${GREEN}[+] RPC daemon started on port 55553${NC}"
fi

# Start Metasploit Web Service if requested
if [ "$START_WEB" = "true" ]; then
    echo -e "${YELLOW}[*] Starting Metasploit Web Service...${NC}"
    msfdb start
    echo -e "${GREEN}[+] Web service started${NC}"
fi

# Update Metasploit if requested
if [ "$UPDATE_MSF" = "true" ]; then
    echo -e "${YELLOW}[*] Updating Metasploit Framework...${NC}"
    msfupdate
    echo -e "${GREEN}[+] Update complete${NC}"
fi

# Load custom modules if they exist
if [ -d "/opt/exploits" ] && [ "$(ls -A /opt/exploits)" ]; then
    echo -e "${YELLOW}[*] Loading custom exploit modules...${NC}"
    cp -r /opt/exploits/* /home/msf/.msf4/modules/exploits/ 2>/dev/null || true
fi

if [ -d "/opt/payloads" ] && [ "$(ls -A /opt/payloads)" ]; then
    echo -e "${YELLOW}[*] Loading custom payload modules...${NC}"
    cp -r /opt/payloads/* /home/msf/.msf4/modules/payloads/ 2>/dev/null || true
fi

# Set up resource scripts
if [ -d "/opt/scripts" ] && [ "$(ls -A /opt/scripts)" ]; then
    echo -e "${YELLOW}[*] Setting up resource scripts...${NC}"
    cp -r /opt/scripts/* /home/msf/.msf4/scripts/ 2>/dev/null || true
fi

# Check if specific exploit/payload is requested
if [ ! -z "$MSF_EXPLOIT" ]; then
    echo -e "${YELLOW}[*] Auto-loading exploit: $MSF_EXPLOIT${NC}"
    
    # Create resource script for auto-exploitation
    cat > /tmp/auto_exploit.rc << EOF
use $MSF_EXPLOIT
set RHOSTS $MSF_RHOSTS
set RPORT $MSF_RPORT
set LHOST $MSF_LHOST
set LPORT $MSF_LPORT
show options
EOF
    
    if [ "$MSF_AUTO_EXPLOIT" = "true" ]; then
        echo "exploit" >> /tmp/auto_exploit.rc
    fi
    
    msfconsole -r /tmp/auto_exploit.rc
    exit 0
fi

# Display container information
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Metasploit Framework Container - Ready${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${YELLOW}  Available Commands:${NC}"
echo -e "    msfconsole          - Start Metasploit Console"
echo -e "    msfvenom            - Payload generator"
echo -e "    msfrpc              - RPC interface"
echo -e "    msfdb               - Database management"
echo -e "${YELLOW}  Environment Variables:${NC}"
echo -e "    START_RPC=true      - Start RPC daemon"
echo -e "    START_WEB=true      - Start web service"
echo -e "    UPDATE_MSF=true     - Update framework"
echo -e "    MSF_EXPLOIT=...     - Auto-load exploit"
echo -e "    MSF_RHOSTS=...      - Target hosts"
echo -e "    MSF_LHOST=...       - Local host"
echo -e "${GREEN}================================================================${NC}"

# Execute the main command
exec "$@"