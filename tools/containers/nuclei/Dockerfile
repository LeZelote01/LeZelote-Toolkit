# Nuclei Vulnerability Scanner Container
# Pentest-USB Toolkit - Docker Configuration
# Version: 1.0.0

FROM golang:1.21-alpine AS builder

LABEL maintainer="Pentest-USB Team"
LABEL description="Nuclei Vulnerability Scanner for Pentest-USB Toolkit"
LABEL version="1.0.0"

# Install build dependencies
RUN apk add --no-cache git

# Build Nuclei from source
WORKDIR /build
RUN git clone https://github.com/projectdiscovery/nuclei.git && \
    cd nuclei && \
    go build -o nuclei

# Production stage
FROM alpine:3.18

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    curl \
    wget \
    nmap \
    netcat-openbsd \
    bind-tools \
    jq \
    python3 \
    py3-pip \
    bash \
    git

# Create nuclei user
RUN adduser -D -s /bin/bash nuclei

# Copy nuclei binary from builder
COPY --from=builder /build/nuclei/nuclei /usr/local/bin/nuclei
RUN chmod +x /usr/local/bin/nuclei

# Create necessary directories
RUN mkdir -p \
    /home/nuclei/.config/nuclei \
    /home/nuclei/templates \
    /home/nuclei/reports \
    /home/nuclei/wordlists \
    /home/nuclei/scripts \
    /opt/nuclei-templates

# Download and install nuclei templates
RUN git clone https://github.com/projectdiscovery/nuclei-templates.git /opt/nuclei-templates && \
    chown -R nuclei:nuclei /opt/nuclei-templates

# Copy configuration file
COPY config.yaml /home/nuclei/.config/nuclei/config.yaml

# Create custom nuclei configuration
RUN cat > /home/nuclei/.config/nuclei/config.yaml << 'EOF'
# Nuclei Configuration File
# Pentest-USB Toolkit Integration

# Templates configuration
templates:
  - /opt/nuclei-templates
  - /home/nuclei/templates

# Update configuration
update-templates: true
update-directory: /opt/nuclei-templates

# Nuclei configuration
verbose: true
no-color: false
silent: false
json: false
include-rr: false

# Network configuration
timeout: 10
retries: 3
rate-limit: 150
bulk-size: 25
templated-requests: 100

# Output configuration
output: /home/nuclei/reports/
markdown-export: /home/nuclei/reports/
json-export: /home/nuclei/reports/
sarif-export: /home/nuclei/reports/

# Severity filtering
severity: 
  - info
  - low  
  - medium
  - high
  - critical

# Tags to include/exclude
include-tags: []
exclude-tags: []

# Custom headers
header:
  - "User-Agent: Nuclei-Pentest-USB/1.0"

# Follow redirects
follow-redirects: true
max-redirects: 10

# Disable cluster
disable-clustering: false

# Custom certificate authority
system-resolvers: false

# Statistics
stats: true
stats-interval: 5

# Metrics
metrics: false
metrics-port: 9092

# Debug configuration
debug: false
debug-req: false
debug-resp: false

# Project file
project: false
project-path: /home/nuclei/.config/nuclei/

# Resume configuration
resume: /home/nuclei/.config/nuclei/resume.cfg

# Exclude hosts
exclude-hosts: []

# Include hosts  
include-hosts: []

# Custom payloads
payloads: /home/nuclei/payloads/

# Interactsh configuration
no-interactsh: false
interactsh-url: ""
interactsh-token: ""

# Rate limit configuration
rate-limit-minute: 0

# Cloud configuration
cloud-upload: false
scan-list: /home/nuclei/targets.txt
EOF

# Install Python dependencies for automation
RUN pip3 install \
    requests \
    urllib3 \
    pyyaml \
    json5

# Create automation scripts
RUN mkdir -p /opt/nuclei-scripts

# Create Nuclei automation script
RUN cat > /opt/nuclei-scripts/nuclei-automation.py << 'EOF'
#!/usr/bin/env python3
"""
Nuclei Automation Script
Pentest-USB Toolkit Integration
"""

import os
import sys
import json
import subprocess
import argparse
import yaml
from pathlib import Path

class NucleiAutomation:
    def __init__(self):
        self.nuclei_bin = "/usr/local/bin/nuclei"
        self.templates_dir = "/opt/nuclei-templates"
        self.config_file = "/home/nuclei/.config/nuclei/config.yaml"
        self.reports_dir = "/home/nuclei/reports"
        
    def update_templates(self):
        """Update nuclei templates"""
        print("[+] Updating Nuclei templates...")
        
        cmd = [self.nuclei_bin, "-update-templates", "-update-directory", self.templates_dir]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("[+] Templates updated successfully")
                return True
            else:
                print(f"[-] Error updating templates: {result.stderr}")
                return False
        except Exception as e:
            print(f"[-] Exception updating templates: {e}")
            return False
    
    def run_scan(self, target, severity=None, tags=None, templates=None, output_format="json"):
        """Run nuclei scan on target"""
        print(f"[+] Starting Nuclei scan on {target}")
        
        # Base command
        cmd = [
            self.nuclei_bin,
            "-target", target,
            "-config", self.config_file,
            "-stats",
            "-silent"
        ]
        
        # Add severity filter
        if severity:
            for sev in severity:
                cmd.extend(["-severity", sev])
        
        # Add tags filter
        if tags:
            for tag in tags:
                cmd.extend(["-tags", tag])
        
        # Add specific templates
        if templates:
            for template in templates:
                cmd.extend(["-templates", template])
        
        # Set output format
        timestamp = int(__import__('time').time())
        output_file = f"{self.reports_dir}/nuclei-scan-{timestamp}"
        
        if output_format == "json":
            cmd.extend(["-json", "-output", f"{output_file}.json"])
        elif output_format == "markdown":
            cmd.extend(["-markdown-export", f"{output_file}.md"])
        elif output_format == "sarif":
            cmd.extend(["-sarif-export", f"{output_file}.sarif"])
        else:
            cmd.extend(["-output", f"{output_file}.txt"])
        
        try:
            print(f"[*] Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[+] Scan completed successfully")
                
                # Parse results if JSON
                if output_format == "json" and os.path.exists(f"{output_file}.json"):
                    return self.parse_json_results(f"{output_file}.json")
                else:
                    return {"output_file": f"{output_file}.{output_format}"}
            else:
                print(f"[-] Scan failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"[-] Exception during scan: {e}")
            return None
    
    def parse_json_results(self, json_file):
        """Parse JSON results and return summary"""
        try:
            with open(json_file, 'r') as f:
                results = []
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))
            
            # Summarize results
            summary = {
                "total_findings": len(results),
                "severity_breakdown": {},
                "top_vulnerabilities": [],
                "affected_hosts": set(),
                "file": json_file
            }
            
            for result in results:
                # Count by severity
                severity = result.get('info', {}).get('severity', 'unknown')
                summary['severity_breakdown'][severity] = summary['severity_breakdown'].get(severity, 0) + 1
                
                # Track affected hosts
                if 'host' in result:
                    summary['affected_hosts'].add(result['host'])
                
                # Add to top vulnerabilities
                vuln_info = {
                    'name': result.get('info', {}).get('name', 'Unknown'),
                    'severity': severity,
                    'host': result.get('host', 'Unknown'),
                    'matched': result.get('matched-at', 'Unknown')
                }
                summary['top_vulnerabilities'].append(vuln_info)
            
            # Convert set to list for JSON serialization
            summary['affected_hosts'] = list(summary['affected_hosts'])
            
            return summary
            
        except Exception as e:
            print(f"[-] Error parsing results: {e}")
            return None
    
    def scan_list(self, target_file, **kwargs):
        """Scan multiple targets from file"""
        if not os.path.exists(target_file):
            print(f"[-] Target file not found: {target_file}")
            return None
        
        print(f"[+] Scanning targets from {target_file}")
        
        # Modify command for file input
        cmd = [
            self.nuclei_bin,
            "-list", target_file,
            "-config", self.config_file,
            "-stats"
        ]
        
        # Add other options
        if kwargs.get('severity'):
            for sev in kwargs['severity']:
                cmd.extend(["-severity", sev])
        
        if kwargs.get('tags'):
            for tag in kwargs['tags']:
                cmd.extend(["-tags", tag])
        
        # Output
        timestamp = int(__import__('time').time())
        output_file = f"{self.reports_dir}/nuclei-bulk-scan-{timestamp}.json"
        cmd.extend(["-json", "-output", output_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[+] Bulk scan completed")
                return self.parse_json_results(output_file)
            else:
                print(f"[-] Bulk scan failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"[-] Exception during bulk scan: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Nuclei Automation for Pentest-USB')
    
    parser.add_argument('command', choices=['scan', 'bulk-scan', 'update'], 
                       help='Command to execute')
    parser.add_argument('--target', help='Target URL or IP')
    parser.add_argument('--file', help='File containing list of targets')
    parser.add_argument('--severity', nargs='+', 
                       choices=['info', 'low', 'medium', 'high', 'critical'],
                       help='Filter by severity')
    parser.add_argument('--tags', nargs='+', help='Filter by tags')
    parser.add_argument('--templates', nargs='+', help='Specific templates to use')
    parser.add_argument('--format', choices=['json', 'markdown', 'sarif', 'txt'],
                       default='json', help='Output format')
    
    args = parser.parse_args()
    
    nuclei = NucleiAutomation()
    
    try:
        if args.command == 'update':
            nuclei.update_templates()
            
        elif args.command == 'scan':
            if not args.target:
                print("Error: --target required for scan command")
                sys.exit(1)
            
            result = nuclei.run_scan(
                target=args.target,
                severity=args.severity,
                tags=args.tags,
                templates=args.templates,
                output_format=args.format
            )
            
            if result:
                print("\n[+] Scan Summary:")
                print(json.dumps(result, indent=2))
            
        elif args.command == 'bulk-scan':
            if not args.file:
                print("Error: --file required for bulk-scan command")
                sys.exit(1)
            
            result = nuclei.scan_list(
                target_file=args.file,
                severity=args.severity,
                tags=args.tags,
                templates=args.templates
            )
            
            if result:
                print("\n[+] Bulk Scan Summary:")
                print(json.dumps(result, indent=2))
                
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

RUN chmod +x /opt/nuclei-scripts/nuclei-automation.py

# Create quick scan templates
RUN mkdir -p /home/nuclei/templates/custom

RUN cat > /home/nuclei/templates/custom/pentest-usb-quick.yaml << 'EOF'
id: pentest-usb-quick

info:
  name: Pentest-USB Quick Scan
  author: pentest-usb
  severity: info
  description: Quick vulnerability assessment for Pentest-USB Toolkit
  tags: pentest-usb,quick,recon

requests:
  - method: GET
    path:
      - "{{BaseURL}}"
      - "{{BaseURL}}/robots.txt"
      - "{{BaseURL}}/sitemap.xml"
      - "{{BaseURL}}/.well-known/security.txt"

    matchers-condition: or
    matchers:
      - type: word
        words:
          - "Server:"
          - "X-Powered-By:"
          - "X-AspNet-Version:"
        part: header

      - type: status
        status:
          - 200

    extractors:
      - type: regex
        name: server_info
        regex:
          - 'Server: ([^\r\n]+)'
        part: header

      - type: regex
        name: powered_by
        regex:
          - 'X-Powered-By: ([^\r\n]+)'
        part: header
EOF

# Set proper ownership
RUN chown -R nuclei:nuclei /home/nuclei /opt/nuclei-scripts

# Switch to nuclei user
USER nuclei

# Set working directory
WORKDIR /home/nuclei

# Expose no ports (nuclei is a CLI tool)

# Set environment variables
ENV NUCLEI_CONFIG_FILE=/home/nuclei/.config/nuclei/config.yaml
ENV NUCLEI_TEMPLATES_DIR=/opt/nuclei-templates

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD nuclei -version || exit 1

# Default command
CMD ["nuclei", "-version"]