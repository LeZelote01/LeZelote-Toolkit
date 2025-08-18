# OWASP ZAP (Zed Attack Proxy) Container
# Pentest-USB Toolkit - Docker Configuration
# Version: 1.0.0

FROM openjdk:11-jre-slim

LABEL maintainer="Pentest-USB Team"
LABEL description="OWASP ZAP for Pentest-USB Toolkit"
LABEL version="1.0.0"

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# ZAP version and download URL
ARG ZAP_VERSION=2.14.0
ARG ZAP_DOWNLOAD_URL=https://github.com/zaproxy/zaproxy/releases/download/v${ZAP_VERSION}/ZAP_${ZAP_VERSION}_Linux.tar.gz

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    python3 \
    python3-pip \
    xmlstarlet \
    xvfb \
    x11vnc \
    openbox \
    firefox-esr \
    chromium \
    net-tools \
    netcat \
    nmap \
    nikto \
    dirb \
    gobuster \
    && rm -rf /var/lib/apt/lists/*

# Create zap user
RUN useradd -d /home/zap -m -s /bin/bash zap && \
    echo zap:zap | chpasswd && \
    mkdir -p /home/zap/.vnc && \
    mkdir -p /home/zap/.ZAP

# Set VNC password
RUN echo "zap" | vncpasswd -f > /home/zap/.vnc/passwd && \
    chmod 600 /home/zap/.vnc/passwd && \
    chown -R zap:zap /home/zap

# Download and install ZAP
RUN mkdir -p /opt && \
    cd /opt && \
    wget -q "$ZAP_DOWNLOAD_URL" -O zap.tar.gz && \
    tar -xzf zap.tar.gz && \
    rm zap.tar.gz && \
    mv ZAP_${ZAP_VERSION} zap && \
    chown -R zap:zap /opt/zap

# Install ZAP Python API
RUN pip3 install \
    python-owasp-zap-v2.4 \
    requests \
    lxml \
    beautifulsoup4 \
    selenium

# Install additional ZAP plugins
RUN cd /opt/zap && \
    ./zap.sh -cmd -silent -addoninstall ascanrules && \
    ./zap.sh -cmd -silent -addoninstall pscanrules && \
    ./zap.sh -cmd -silent -addoninstall sqliplugin && \
    ./zap.sh -cmd -silent -addoninstall bruteforce && \
    ./zap.sh -cmd -silent -addoninstall directorylistv1 && \
    ./zap.sh -cmd -silent -addoninstall directorylistv2_3 && \
    ./zap.sh -cmd -silent -addoninstall websocket && \
    ./zap.sh -cmd -silent -addoninstall selenium && \
    ./zap.sh -cmd -silent -addoninstall exportreport && \
    ./zap.sh -cmd -silent -addoninstall alertFilters

# Create ZAP configuration directory and files
RUN mkdir -p /home/zap/.ZAP/config && \
    mkdir -p /home/zap/.ZAP/session && \
    mkdir -p /home/zap/.ZAP/reports && \
    mkdir -p /home/zap/.ZAP/scripts && \
    mkdir -p /home/zap/.ZAP/policies

# Create default ZAP configuration
RUN cat > /home/zap/.ZAP/config/config.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<config>
    <api>
        <key>pentest-usb-zap-key</key>
        <enabled>true</enabled>
        <secure>false</secure>
        <port>8090</port>
        <host>0.0.0.0</host>
    </api>
    <proxy>
        <ip>0.0.0.0</ip>
        <port>8080</port>
        <enabled>true</enabled>
    </proxy>
    <spider>
        <maxDepth>5</spider>
        <threadCount>2</threadCount>
        <maxDuration>60</maxDuration>
        <acceptCookies>true</acceptCookies>
        <handleParameters>true</handleParameters>
    </spider>
    <scanner>
        <strength>MEDIUM</strength>
        <alertThreshold>MEDIUM</alertThreshold>
        <maxRuleDurationInMins>10</maxRuleDurationInMins>
        <delayInMs>0</delayInMs>
    </scanner>
    <reports>
        <format>HTML</format>
        <automaticSave>true</automaticSave>
        <path>/home/zap/.ZAP/reports/</path>
    </reports>
</config>
EOF

# Create custom ZAP policies
RUN cat > /home/zap/.ZAP/policies/pentest-usb-policy.policy << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<policy>
    <name>Pentest-USB Policy</name>
    <description>Custom scanning policy for Pentest-USB Toolkit</description>
    
    <!-- SQL Injection -->
    <scanner id="40018" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    
    <!-- XSS -->
    <scanner id="40012" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    <scanner id="40014" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    <scanner id="40016" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    <scanner id="40017" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    
    <!-- Directory Traversal -->
    <scanner id="6" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    
    <!-- Command Injection -->
    <scanner id="90020" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    
    <!-- CSRF -->
    <scanner id="20012" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    
    <!-- File Upload -->
    <scanner id="7" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    
    <!-- Authentication Bypass -->
    <scanner id="10101" enabled="true" level="MEDIUM" strength="MEDIUM"/>
    
    <!-- Session Management -->
    <scanner id="10202" enabled="true" level="MEDIUM" strength="MEDIUM"/>
</policy>
EOF

# Create ZAP automation scripts
RUN mkdir -p /opt/zap-scripts

RUN cat > /opt/zap-scripts/auto-scan.py << 'EOF'
#!/usr/bin/env python3
"""
ZAP Automated Scanning Script
Pentest-USB Toolkit Integration
"""

import time
import sys
from zapv2 import ZAPv2

def main():
    # Configure ZAP
    zap = ZAPv2(proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})
    
    if len(sys.argv) < 2:
        print("Usage: python3 auto-scan.py <target_url>")
        sys.exit(1)
    
    target = sys.argv[1]
    print(f"[+] Starting automated scan of {target}")
    
    # Spider the target
    print("[*] Starting spider...")
    scan_id = zap.spider.scan(target)
    
    while int(zap.spider.status(scan_id)) < 100:
        print(f"Spider progress: {zap.spider.status(scan_id)}%")
        time.sleep(2)
    
    print("[+] Spider completed")
    
    # Active scan
    print("[*] Starting active scan...")
    scan_id = zap.ascan.scan(target)
    
    while int(zap.ascan.status(scan_id)) < 100:
        print(f"Active scan progress: {zap.ascan.status(scan_id)}%")
        time.sleep(5)
    
    print("[+] Active scan completed")
    
    # Generate report
    print("[*] Generating report...")
    report = zap.core.htmlreport()
    
    with open('/home/zap/.ZAP/reports/scan-report.html', 'w') as f:
        f.write(report)
    
    print("[+] Report saved to /home/zap/.ZAP/reports/scan-report.html")
    
    # Print summary
    alerts = zap.core.alerts()
    print(f"[+] Found {len(alerts)} alerts")

if __name__ == "__main__":
    main()
EOF

RUN chmod +x /opt/zap-scripts/auto-scan.py

# Set proper ownership
RUN chown -R zap:zap /home/zap/.ZAP /opt/zap-scripts

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ZAP ports
EXPOSE 8080 8090 5900

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD netstat -an | grep -q :8080 || exit 1

# Set working directory
WORKDIR /opt/zap

# Switch to zap user
USER zap

# Set environment variables
ENV ZAP_PORT=8080
ENV ZAP_API_PORT=8090
ENV DISPLAY=:1.0

ENTRYPOINT ["/entrypoint.sh"]
CMD ["zap-daemon"]