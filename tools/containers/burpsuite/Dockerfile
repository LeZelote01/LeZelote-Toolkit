# Burp Suite Professional Container
# Pentest-USB Toolkit - Docker Configuration
# Version: 1.0.0

FROM openjdk:11-jre-slim

LABEL maintainer="Pentest-USB Team"
LABEL description="Burp Suite Professional for Pentest-USB Toolkit"
LABEL version="1.0.0"

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    python3 \
    python3-pip \
    xvfb \
    x11vnc \
    openbox \
    fluxbox \
    net-tools \
    netcat \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Create burp user
RUN useradd -d /home/burp -m -s /bin/bash burp && \
    echo burp:burp | chpasswd && \
    mkdir -p /home/burp/.vnc && \
    mkdir -p /home/burp/.BurpSuite

# Set VNC password
RUN echo "burp" | vncpasswd -f > /home/burp/.vnc/passwd && \
    chmod 600 /home/burp/.vnc/passwd && \
    chown -R burp:burp /home/burp

# Download and install Burp Suite Professional
# Note: This requires a valid Burp Suite Professional license
ARG BURP_VERSION=2023.10.3.7
ARG BURP_DOWNLOAD_URL="https://portswigger.net/burp/releases/download?product=pro&version=${BURP_VERSION}&type=Jar"

# Create installation directory
RUN mkdir -p /opt/burpsuite && \
    chown -R burp:burp /opt/burpsuite

# Download Burp Suite (placeholder - requires actual download)
# In real deployment, you would need to download from PortSwigger with proper credentials
COPY burpsuite_pro.jar /opt/burpsuite/burpsuite_pro.jar

# Alternative: Use wget to download (requires proper URL and access)
# RUN wget -O /opt/burpsuite/burpsuite_pro.jar "$BURP_DOWNLOAD_URL"

# Make burpsuite executable
RUN chmod +x /opt/burpsuite/burpsuite_pro.jar && \
    chown burp:burp /opt/burpsuite/burpsuite_pro.jar

# Install Python dependencies for automation
RUN pip3 install \
    requests \
    urllib3 \
    beautifulsoup4 \
    lxml

# Create Burp Suite configuration
RUN mkdir -p /home/burp/.BurpSuite/config

# Copy configuration file
COPY burp.config /home/burp/.BurpSuite/config/burp.config

# Create default Burp configuration
RUN cat > /home/burp/.BurpSuite/config/user.json << 'EOF'
{
  "proxy": {
    "request_listeners": [
      {
        "certificate_mode": "per_host",
        "listen_mode": "all_interfaces",
        "listen_port": 8080,
        "listen_specific_address": "",
        "protocol": "http",
        "running": true
      }
    ],
    "response_modification": {
      "enable_response_streaming": true
    },
    "ssl": {
      "negotiation_fail_action": "ignore",
      "client_ssl_certificates": []
    }
  },
  "scanner": {
    "live_scanning": {
      "live_audit": {
        "enabled": false
      },
      "live_passive_crawl": {
        "enabled": true
      }
    },
    "reporting": {
      "make_http_requests": true
    }
  },
  "repeater": {
    "ssl": {
      "override_user_options": false
    }
  },
  "intruder": {
    "request_engine": {
      "threads_per_connection": 1,
      "retry_on_network_failure": true,
      "pause_before_retry": 2000,
      "throttle_between_requests": 0,
      "start_paused": false
    }
  },
  "project_options": {
    "misc": {
      "scheduled_tasks": {
        "pause_spider_and_scanner_when_proxy_idle": false
      },
      "logging": {
        "requests_and_responses": {
          "enabled": true,
          "log_in_tool_suite": ["proxy", "spider", "scanner", "intruder", "repeater"]
        }
      }
    },
    "http": {
      "redirections": {
        "understand_any_status_code_as_redirection": false,
        "maximum_redirections": 10
      },
      "streaming_responses": {
        "strip_chunked_encoding_metadata": true,
        "store_streaming_responses": true
      }
    }
  }
}
EOF

# Create Burp automation scripts
RUN mkdir -p /opt/burp-scripts

RUN cat > /opt/burp-scripts/burp-automation.py << 'EOF'
#!/usr/bin/env python3
"""
Burp Suite Automation Script
Pentest-USB Toolkit Integration
"""

import os
import sys
import json
import time
import requests
import argparse
import subprocess
from urllib.parse import urljoin

class BurpAutomation:
    def __init__(self, api_url="http://127.0.0.1:1337", api_key=""):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})
    
    def _request(self, method, endpoint, **kwargs):
        """Make API request to Burp"""
        url = urljoin(self.api_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"[-] API request failed: {e}")
            return None
    
    def spider_scan(self, target_url):
        """Start spider scan on target"""
        print(f"[+] Starting spider scan on {target_url}")
        
        data = {
            "baseUrl": target_url
        }
        
        result = self._request("POST", "/v0.1/scan", json=data)
        
        if result:
            task_id = result.get("taskId")
            print(f"[+] Spider scan started with task ID: {task_id}")
            return task_id
        
        return None
    
    def active_scan(self, target_url):
        """Start active scan on target"""
        print(f"[+] Starting active scan on {target_url}")
        
        data = {
            "baseUrl": target_url,
            "scanType": "active"
        }
        
        result = self._request("POST", "/v0.1/scan", json=data)
        
        if result:
            task_id = result.get("taskId")
            print(f"[+] Active scan started with task ID: {task_id}")
            return task_id
        
        return None
    
    def get_scan_status(self, task_id):
        """Get scan status"""
        result = self._request("GET", f"/v0.1/scan/{task_id}")
        
        if result:
            status = result.get("scanStatus", "unknown")
            progress = result.get("scanMetrics", {}).get("crawlRequestsMade", 0)
            return {"status": status, "progress": progress}
        
        return None
    
    def get_scan_issues(self, task_id):
        """Get scan issues/vulnerabilities"""
        result = self._request("GET", f"/v0.1/scan/{task_id}")
        
        if result:
            issues = result.get("issue_events", [])
            
            vulnerabilities = []
            for issue in issues:
                vuln = {
                    "name": issue.get("issue", {}).get("name", "Unknown"),
                    "severity": issue.get("issue", {}).get("severity", "Unknown"),
                    "confidence": issue.get("issue", {}).get("confidence", "Unknown"),
                    "url": issue.get("issue", {}).get("origin", "Unknown"),
                    "description": issue.get("issue", {}).get("background", "No description")
                }
                vulnerabilities.append(vuln)
            
            return vulnerabilities
        
        return []
    
    def generate_report(self, task_id, report_type="html"):
        """Generate scan report"""
        print(f"[+] Generating {report_type} report for task {task_id}")
        
        data = {
            "reportType": report_type
        }
        
        result = self._request("POST", f"/v0.1/scan/{task_id}/report", json=data)
        
        if result:
            report_id = result.get("reportId")
            print(f"[+] Report generation started with ID: {report_id}")
            
            # Wait for report generation
            while True:
                status_result = self._request("GET", f"/v0.1/scan/{task_id}/report/{report_id}")
                
                if status_result:
                    status = status_result.get("status", "unknown")
                    
                    if status == "succeeded":
                        download_url = status_result.get("downloadUrl")
                        print(f"[+] Report ready for download: {download_url}")
                        return download_url
                    elif status == "failed":
                        print("[-] Report generation failed")
                        return None
                    else:
                        print(f"[*] Report generation in progress: {status}")
                        time.sleep(10)
                else:
                    print("[-] Failed to get report status")
                    return None
        
        return None

def start_burp_headless():
    """Start Burp Suite in headless mode"""
    print("[+] Starting Burp Suite in headless mode...")
    
    cmd = [
        "java", "-jar", "/opt/burpsuite/burpsuite_pro.jar",
        "--headless",
        "--config-file", "/home/burp/.BurpSuite/config/burp.config",
        "--project-file", "/home/burp/.BurpSuite/pentest-usb-project.burp"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            user="burp"
        )
        
        print(f"[+] Burp Suite started with PID: {process.pid}")
        
        # Wait for Burp to be ready
        print("[*] Waiting for Burp Suite API to be ready...")
        for i in range(30):
            try:
                response = requests.get("http://127.0.0.1:1337/v0.1/", timeout=5)
                if response.status_code == 200:
                    print("[+] Burp Suite API is ready")
                    return process
            except:
                pass
            
            time.sleep(2)
        
        print("[-] Burp Suite API did not become ready in time")
        return None
        
    except Exception as e:
        print(f"[-] Failed to start Burp Suite: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Burp Suite Automation for Pentest-USB')
    
    parser.add_argument('command', choices=['start', 'spider', 'scan', 'status', 'issues', 'report'])
    parser.add_argument('--target', help='Target URL')
    parser.add_argument('--task-id', help='Task ID for status/issues/report commands')
    parser.add_argument('--report-type', choices=['html', 'xml'], default='html', help='Report format')
    parser.add_argument('--api-url', default='http://127.0.0.1:1337', help='Burp API URL')
    parser.add_argument('--api-key', default='', help='Burp API key')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'start':
            start_burp_headless()
            
        else:
            burp = BurpAutomation(args.api_url, args.api_key)
            
            if args.command == 'spider':
                if not args.target:
                    print("Error: --target required for spider command")
                    sys.exit(1)
                
                task_id = burp.spider_scan(args.target)
                if task_id:
                    print(f"Spider scan started. Task ID: {task_id}")
                    print(f"Monitor with: python3 {sys.argv[0]} status --task-id {task_id}")
                
            elif args.command == 'scan':
                if not args.target:
                    print("Error: --target required for scan command")
                    sys.exit(1)
                
                task_id = burp.active_scan(args.target)
                if task_id:
                    print(f"Active scan started. Task ID: {task_id}")
                    print(f"Monitor with: python3 {sys.argv[0]} status --task-id {task_id}")
                
            elif args.command == 'status':
                if not args.task_id:
                    print("Error: --task-id required for status command")
                    sys.exit(1)
                
                status = burp.get_scan_status(args.task_id)
                if status:
                    print(f"Status: {status['status']}")
                    print(f"Progress: {status['progress']} requests made")
                
            elif args.command == 'issues':
                if not args.task_id:
                    print("Error: --task-id required for issues command")
                    sys.exit(1)
                
                issues = burp.get_scan_issues(args.task_id)
                
                print(f"Found {len(issues)} issues:")
                for i, issue in enumerate(issues, 1):
                    print(f"\n{i}. {issue['name']}")
                    print(f"   Severity: {issue['severity']}")
                    print(f"   Confidence: {issue['confidence']}")
                    print(f"   URL: {issue['url']}")
                    print(f"   Description: {issue['description'][:100]}...")
                
            elif args.command == 'report':
                if not args.task_id:
                    print("Error: --task-id required for report command")
                    sys.exit(1)
                
                report_url = burp.generate_report(args.task_id, args.report_type)
                if report_url:
                    print(f"Report available at: {report_url}")
                    
    except KeyboardInterrupt:
        print("\n[!] Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

RUN chmod +x /opt/burp-scripts/burp-automation.py

# Create startup script
RUN cat > /start-burp.sh << 'EOF'
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[+] Starting Burp Suite Professional Container${NC}"
echo -e "${GREEN}[+] Pentest-USB Toolkit Integration${NC}"

# Function to start VNC server
start_vnc() {
    echo -e "${YELLOW}[*] Starting VNC server...${NC}"
    Xvfb :1 -screen 0 1024x768x16 &
    x11vnc -display :1 -nopw -listen 0.0.0.0 -xkb -ncache 10 -ncache_cr -forever &
    fluxbox &
    echo -e "${GREEN}[+] VNC server started on port 5900${NC}"
    export DISPLAY=:1
}

# Function to start Burp Suite GUI
start_burp_gui() {
    echo -e "${YELLOW}[*] Starting Burp Suite GUI...${NC}"
    
    cd /opt/burpsuite
    
    java -jar burpsuite_pro.jar \
        --config-file=/home/burp/.BurpSuite/config/burp.config \
        --project-file=/home/burp/.BurpSuite/pentest-usb-project.burp
}

# Function to start Burp Suite headless
start_burp_headless() {
    echo -e "${YELLOW}[*] Starting Burp Suite in headless mode...${NC}"
    
    cd /opt/burpsuite
    
    java -jar burpsuite_pro.jar \
        --headless \
        --config-file=/home/burp/.BurpSuite/config/burp.config \
        --project-file=/home/burp/.BurpSuite/pentest-usb-project.burp
}

# Display container information
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Burp Suite Professional Container - Ready${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${YELLOW}  Proxy:             http://localhost:8080${NC}"
echo -e "${YELLOW}  API:               http://localhost:1337${NC}"

if [ "$START_VNC" = "true" ]; then
    echo -e "${YELLOW}  VNC Server:        vnc://localhost:5900${NC}"
    echo -e "${YELLOW}  VNC Password:      burp${NC}"
fi

echo -e "${YELLOW}  Available Commands:${NC}"
echo -e "    burp-gui           - Start Burp with GUI (requires VNC)"
echo -e "    burp-headless      - Start Burp in headless mode"
echo -e "    burp-automation.py - Automation script"
echo -e "${YELLOW}  Environment Variables:${NC}"
echo -e "    START_VNC=true     - Start VNC server for GUI"
echo -e "    START_HEADLESS=true - Start in headless mode"
echo -e "    AUTO_SCAN_TARGET=... - Auto-scan target URL"
echo -e "${GREEN}================================================================${NC}"

# Start VNC if requested
if [ "$START_VNC" = "true" ]; then
    start_vnc
fi

# Handle different startup modes
if [ "$START_HEADLESS" = "true" ]; then
    start_burp_headless
elif [ "$START_VNC" = "true" ]; then
    start_burp_gui
else
    # Default to showing help
    echo -e "${YELLOW}[*] Burp Suite container ready${NC}"
    echo -e "${YELLOW}[*] Use environment variables to control startup mode${NC}"
    
    # Keep container running
    tail -f /dev/null
fi
EOF

RUN chmod +x /start-burp.sh

# Set proper ownership
RUN chown -R burp:burp /home/burp /opt/burp-scripts

# Switch to burp user
USER burp

# Expose Burp Suite ports
EXPOSE 8080 1337 5900

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD netstat -an | grep -q :8080 || exit 1

# Set working directory
WORKDIR /opt/burpsuite

# Set environment variables
ENV DISPLAY=:1.0
ENV BURP_CONFIG_FILE=/home/burp/.BurpSuite/config/burp.config

CMD ["/start-burp.sh"]