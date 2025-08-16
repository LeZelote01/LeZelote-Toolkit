#!/bin/bash
# OWASP ZAP Entrypoint Script
# Pentest-USB Toolkit - Docker Configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[+] Starting OWASP ZAP Container${NC}"
echo -e "${GREEN}[+] Pentest-USB Toolkit - Version 1.0.0${NC}"

# Set default values
ZAP_PORT=${ZAP_PORT:-8080}
ZAP_API_PORT=${ZAP_API_PORT:-8090}
ZAP_HOST=${ZAP_HOST:-0.0.0.0}

# Start VNC server for GUI access if requested
if [ "$START_VNC" = "true" ]; then
    echo -e "${YELLOW}[*] Starting VNC server...${NC}"
    Xvfb :1 -screen 0 1024x768x16 &
    x11vnc -display :1 -nopw -listen 0.0.0.0 -xkb -ncache 10 -ncache_cr -forever &
    openbox &
    echo -e "${GREEN}[+] VNC server started on port 5900${NC}"
fi

# Function to start ZAP daemon
start_zap_daemon() {
    echo -e "${YELLOW}[*] Starting ZAP daemon...${NC}"
    
    cd /opt/zap
    
    # ZAP daemon command
    ZAP_CMD="./zap.sh -daemon -host ${ZAP_HOST} -port ${ZAP_PORT} -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true -config api.key=pentest-usb-zap-key"
    
    # Add configuration options
    ZAP_CMD="${ZAP_CMD} -config scanner.strength=MEDIUM"
    ZAP_CMD="${ZAP_CMD} -config scanner.alertThreshold=MEDIUM"
    ZAP_CMD="${ZAP_CMD} -config spider.maxDepth=5"
    ZAP_CMD="${ZAP_CMD} -config spider.threadCount=2"
    
    # Add custom policy if exists
    if [ -f "/home/zap/.ZAP/policies/pentest-usb-policy.policy" ]; then
        ZAP_CMD="${ZAP_CMD} -config scanner.policy=pentest-usb-policy"
    fi
    
    echo -e "${YELLOW}[*] Executing: ${ZAP_CMD}${NC}"
    exec $ZAP_CMD
}

# Function to start ZAP with GUI
start_zap_gui() {
    echo -e "${YELLOW}[*] Starting ZAP with GUI...${NC}"
    
    cd /opt/zap
    
    # Start ZAP GUI (requires VNC)
    ./zap.sh -host ${ZAP_HOST} -port ${ZAP_PORT} -config api.key=pentest-usb-zap-key
}

# Function to run automated scan
run_auto_scan() {
    echo -e "${YELLOW}[*] Running automated scan on: ${AUTO_SCAN_TARGET}${NC}"
    
    # Wait for ZAP to start
    sleep 10
    
    # Run the automation script
    python3 /opt/zap-scripts/auto-scan.py "${AUTO_SCAN_TARGET}"
}

# Function to update ZAP
update_zap() {
    echo -e "${YELLOW}[*] Updating ZAP add-ons...${NC}"
    
    cd /opt/zap
    
    # Update all add-ons
    ./zap.sh -cmd -silent -addonUpdate
    
    echo -e "${GREEN}[+] ZAP update complete${NC}"
}

# Update ZAP if requested
if [ "$UPDATE_ZAP" = "true" ]; then
    update_zap
fi

# Check if specific scan target is provided
if [ ! -z "$AUTO_SCAN_TARGET" ]; then
    # Start ZAP daemon in background
    start_zap_daemon &
    
    # Wait for ZAP to be ready
    echo -e "${YELLOW}[*] Waiting for ZAP to be ready...${NC}"
    
    # Wait for ZAP API to be available
    for i in {1..30}; do
        if curl -s "http://localhost:${ZAP_API_PORT}/JSON/core/view/version/" > /dev/null 2>&1; then
            echo -e "${GREEN}[+] ZAP is ready${NC}"
            break
        fi
        echo -e "${YELLOW}[*] Waiting for ZAP... (${i}/30)${NC}"
        sleep 2
    done
    
    # Run automated scan
    run_auto_scan
    
    # Keep container running
    tail -f /dev/null
fi

# Display container information
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  OWASP ZAP Container - Ready${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${YELLOW}  ZAP Proxy:          http://localhost:${ZAP_PORT}${NC}"
echo -e "${YELLOW}  ZAP API:            http://localhost:${ZAP_API_PORT}${NC}"
echo -e "${YELLOW}  API Key:            pentest-usb-zap-key${NC}"

if [ "$START_VNC" = "true" ]; then
    echo -e "${YELLOW}  VNC Server:         vnc://localhost:5900${NC}"
    echo -e "${YELLOW}  VNC Password:       zap${NC}"
fi

echo -e "${YELLOW}  Available Commands:${NC}"
echo -e "    zap-daemon          - Start ZAP daemon"
echo -e "    zap-gui             - Start ZAP GUI (requires VNC)"
echo -e "    auto-scan.py        - Automated scanning script"
echo -e "${YELLOW}  Environment Variables:${NC}"
echo -e "    START_VNC=true      - Start VNC server for GUI"
echo -e "    UPDATE_ZAP=true     - Update ZAP add-ons"
echo -e "    AUTO_SCAN_TARGET=...  - Auto-scan target URL"
echo -e "${GREEN}================================================================${NC}"

# Handle different commands
case "$1" in
    "zap-daemon")
        start_zap_daemon
        ;;
    "zap-gui")
        start_zap_gui
        ;;
    "bash"|"sh")
        exec "$@"
        ;;
    *)
        start_zap_daemon
        ;;
esac