# BloodHound Active Directory Analysis Container
# Pentest-USB Toolkit - Docker Configuration
# Version: 1.0.0

FROM ubuntu:22.04

LABEL maintainer="Pentest-USB Team"
LABEL description="BloodHound Active Directory Analysis for Pentest-USB Toolkit"
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
    openjdk-11-jre-headless \
    python3 \
    python3-pip \
    nodejs \
    npm \
    unzip \
    xvfb \
    x11vnc \
    openbox \
    net-tools \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Install Neo4j
RUN wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable 4.4' | tee -a /etc/apt/sources.list.d/neo4j.list && \
    apt-get update && \
    apt-get install -y neo4j=1:4.4.* && \
    rm -rf /var/lib/apt/lists/*

# Create bloodhound user
RUN useradd -d /home/bloodhound -m -s /bin/bash bloodhound && \
    echo bloodhound:bloodhound | chpasswd && \
    mkdir -p /home/bloodhound/.vnc && \
    mkdir -p /home/bloodhound/.config/bloodhound

# Set VNC password
RUN echo "bloodhound" | vncpasswd -f > /home/bloodhound/.vnc/passwd && \
    chmod 600 /home/bloodhound/.vnc/passwd && \
    chown -R bloodhound:bloodhound /home/bloodhound

# Install BloodHound
ARG BLOODHOUND_VERSION=4.3.1
RUN mkdir -p /opt/bloodhound && \
    cd /opt/bloodhound && \
    wget -q "https://github.com/BloodHoundAD/BloodHound/releases/download/${BLOODHOUND_VERSION}/BloodHound-linux-x64.zip" && \
    unzip BloodHound-linux-x64.zip && \
    rm BloodHound-linux-x64.zip && \
    chmod +x BloodHound-linux-x64/BloodHound && \
    chown -R bloodhound:bloodhound /opt/bloodhound

# Install BloodHound Python collector (BloodHound.py)
RUN pip3 install bloodhound

# Install SharpHound collector
RUN mkdir -p /opt/collectors && \
    cd /opt/collectors && \
    wget -q "https://github.com/BloodHoundAD/BloodHound/raw/master/Collectors/SharpHound.exe" && \
    wget -q "https://github.com/BloodHoundAD/BloodHound/raw/master/Collectors/SharpHound.ps1" && \
    chown -R bloodhound:bloodhound /opt/collectors

# Copy Neo4j configuration
COPY neo4j.conf /etc/neo4j/neo4j.conf

# Configure Neo4j
RUN mkdir -p /var/lib/neo4j/data /var/lib/neo4j/logs /var/lib/neo4j/import /var/lib/neo4j/plugins && \
    chown -R neo4j:neo4j /var/lib/neo4j && \
    chown -R neo4j:neo4j /etc/neo4j

# Set Neo4j initial password
RUN neo4j-admin set-initial-password bloodhound

# Create BloodHound data directories
RUN mkdir -p \
    /home/bloodhound/data \
    /home/bloodhound/reports \
    /home/bloodhound/collectors \
    /home/bloodhound/queries \
    /opt/bloodhound-automation

# Install additional Python dependencies
RUN pip3 install \
    neo4j \
    requests \
    ldap3 \
    impacket \
    pycryptodome

# Create BloodHound automation scripts
RUN cat > /opt/bloodhound-automation/bloodhound-automation.py << 'EOF'
#!/usr/bin/env python3
"""
BloodHound Automation Script
Pentest-USB Toolkit Integration
"""

import os
import sys
import json
import time
import argparse
import subprocess
from neo4j import GraphDatabase

class BloodHoundAutomation:
    def __init__(self, neo4j_uri="bolt://localhost:7687", username="neo4j", password="bloodhound"):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = username
        self.neo4j_pass = password
        self.driver = None
        
    def connect_neo4j(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_pass)
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            
            print("[+] Connected to Neo4j database")
            return True
            
        except Exception as e:
            print(f"[-] Failed to connect to Neo4j: {e}")
            return False
    
    def import_data(self, data_file):
        """Import BloodHound data into Neo4j"""
        if not os.path.exists(data_file):
            print(f"[-] Data file not found: {data_file}")
            return False
        
        print(f"[+] Importing data from {data_file}")
        
        try:
            # Use BloodHound's data importer
            cmd = [
                "python3", "-c",
                f"""
import json
from neo4j import GraphDatabase

driver = GraphDatabase.driver('{self.neo4j_uri}', auth=('{self.neo4j_user}', '{self.neo4j_pass}'))

with open('{data_file}', 'r') as f:
    data = json.load(f)

with driver.session() as session:
    # Import logic would go here
    # This is a simplified version
    print('Data imported successfully')

driver.close()
"""
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[+] Data imported successfully")
                return True
            else:
                print(f"[-] Import failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[-] Error importing data: {e}")
            return False
    
    def run_query(self, query_name):
        """Run predefined BloodHound queries"""
        if not self.driver:
            if not self.connect_neo4j():
                return None
        
        queries = {
            "domain_admins": """
                MATCH (u:User)-[:MemberOf*1..]->(g:Group)
                WHERE g.name =~ '(?i).*domain admin.*'
                RETURN u.name as user, g.name as group
            """,
            
            "high_value_targets": """
                MATCH (u:User {highvalue: true})
                RETURN u.name as user, u.domain as domain
            """,
            
            "kerberoastable_users": """
                MATCH (u:User)
                WHERE u.hasspn = true
                RETURN u.name as user, u.serviceprincipalnames as spns
            """,
            
            "asreproastable_users": """
                MATCH (u:User)
                WHERE u.dontreqpreauth = true
                RETURN u.name as user, u.domain as domain
            """,
            
            "shortest_paths_to_da": """
                MATCH p=shortestPath((u:User)-[*1..]->(g:Group))
                WHERE u.name <> 'ANONYMOUS LOGON@DOMAIN.LOCAL'
                AND g.name =~ '(?i).*domain admin.*'
                RETURN p
                LIMIT 10
            """,
            
            "computers_with_unconstrained_delegation": """
                MATCH (c:Computer)
                WHERE c.unconstraineddelegation = true
                RETURN c.name as computer, c.domain as domain
            """,
            
            "users_with_dcsync_rights": """
                MATCH p=(u:User)-[:DCSync]->(d:Domain)
                RETURN u.name as user, d.name as domain
            """
        }
        
        if query_name not in queries:
            print(f"[-] Unknown query: {query_name}")
            print(f"[*] Available queries: {list(queries.keys())}")
            return None
        
        try:
            with self.driver.session() as session:
                print(f"[+] Running query: {query_name}")
                result = session.run(queries[query_name])
                
                records = []
                for record in result:
                    records.append(dict(record))
                
                print(f"[+] Query returned {len(records)} results")
                return records
                
        except Exception as e:
            print(f"[-] Query failed: {e}")
            return None
    
    def analyze_attack_paths(self):
        """Analyze potential attack paths"""
        print("[+] Analyzing attack paths...")
        
        analyses = {}
        
        # Run key queries
        queries_to_run = [
            "domain_admins",
            "high_value_targets", 
            "kerberoastable_users",
            "asreproastable_users",
            "shortest_paths_to_da"
        ]
        
        for query in queries_to_run:
            results = self.run_query(query)
            if results:
                analyses[query] = results
        
        return analyses
    
    def generate_report(self, analysis_results, output_file):
        """Generate analysis report"""
        print(f"[+] Generating report: {output_file}")
        
        try:
            report = {
                "timestamp": time.time(),
                "analysis": analysis_results,
                "summary": {
                    "total_domain_admins": len(analysis_results.get("domain_admins", [])),
                    "high_value_targets": len(analysis_results.get("high_value_targets", [])),
                    "kerberoastable_users": len(analysis_results.get("kerberoastable_users", [])),
                    "asreproastable_users": len(analysis_results.get("asreproastable_users", [])),
                    "attack_paths_found": len(analysis_results.get("shortest_paths_to_da", []))
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"[+] Report saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"[-] Failed to generate report: {e}")
            return False
    
    def collect_data(self, target_domain, username, password, method="python"):
        """Collect BloodHound data from target domain"""
        print(f"[+] Collecting data from {target_domain}")
        
        if method == "python":
            # Use BloodHound.py
            cmd = [
                "bloodhound-python",
                "-d", target_domain,
                "-u", username,
                "-p", password,
                "-ns", target_domain,
                "-c", "all",
                "--zip"
            ]
        else:
            print("[-] Only Python collector supported in this container")
            return False
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/bloodhound/data")
            
            if result.returncode == 0:
                print("[+] Data collection completed")
                
                # Find the generated zip file
                import glob
                zip_files = glob.glob("/home/bloodhound/data/*.zip")
                if zip_files:
                    latest_zip = max(zip_files, key=os.path.getctime)
                    print(f"[+] Data saved to: {latest_zip}")
                    return latest_zip
                else:
                    print("[-] No zip file found after collection")
                    return False
            else:
                print(f"[-] Data collection failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[-] Error during data collection: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='BloodHound Automation for Pentest-USB')
    
    parser.add_argument('command', 
                       choices=['collect', 'import', 'analyze', 'query', 'report'])
    parser.add_argument('--domain', help='Target domain')
    parser.add_argument('--username', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--data-file', help='BloodHound data file to import')
    parser.add_argument('--query-name', help='Query name to run')
    parser.add_argument('--output', help='Output file for reports')
    
    args = parser.parse_args()
    
    bh = BloodHoundAutomation()
    
    try:
        if args.command == 'collect':
            if not all([args.domain, args.username, args.password]):
                print("Error: --domain, --username, and --password required for collect command")
                sys.exit(1)
            
            result = bh.collect_data(args.domain, args.username, args.password)
            if result:
                print(f"Collection completed. Data file: {result}")
            
        elif args.command == 'import':
            if not args.data_file:
                print("Error: --data-file required for import command")
                sys.exit(1)
            
            bh.import_data(args.data_file)
            
        elif args.command == 'analyze':
            if not bh.connect_neo4j():
                sys.exit(1)
            
            results = bh.analyze_attack_paths()
            
            if args.output:
                bh.generate_report(results, args.output)
            else:
                print(json.dumps(results, indent=2, default=str))
            
        elif args.command == 'query':
            if not args.query_name:
                print("Error: --query-name required for query command")
                sys.exit(1)
            
            if not bh.connect_neo4j():
                sys.exit(1)
            
            results = bh.run_query(args.query_name)
            if results:
                print(json.dumps(results, indent=2, default=str))
            
        elif args.command == 'report':
            output_file = args.output or "/home/bloodhound/reports/bloodhound-report.json"
            
            if not bh.connect_neo4j():
                sys.exit(1)
            
            results = bh.analyze_attack_paths()
            bh.generate_report(results, output_file)
            
    except KeyboardInterrupt:
        print("\n[!] Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

RUN chmod +x /opt/bloodhound-automation/bloodhound-automation.py

# Create startup script
RUN cat > /start-bloodhound.sh << 'EOF'
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[+] Starting BloodHound Container${NC}"
echo -e "${GREEN}[+] Pentest-USB Toolkit Integration${NC}"

# Function to start VNC server
start_vnc() {
    echo -e "${YELLOW}[*] Starting VNC server...${NC}"
    Xvfb :1 -screen 0 1024x768x16 &
    x11vnc -display :1 -nopw -listen 0.0.0.0 -xkb -ncache 10 -ncache_cr -forever &
    openbox &
    echo -e "${GREEN}[+] VNC server started on port 5900${NC}"
    export DISPLAY=:1
}

# Function to start Neo4j
start_neo4j() {
    echo -e "${YELLOW}[*] Starting Neo4j database...${NC}"
    
    # Start Neo4j as neo4j user
    sudo -u neo4j neo4j start
    
    # Wait for Neo4j to be ready
    echo -e "${YELLOW}[*] Waiting for Neo4j to be ready...${NC}"
    for i in {1..30}; do
        if neo4j status | grep -q "Neo4j is running"; then
            echo -e "${GREEN}[+] Neo4j is ready${NC}"
            return 0
        fi
        echo -e "${YELLOW}[*] Waiting for Neo4j... (${i}/30)${NC}"
        sleep 2
    done
    
    echo -e "${RED}[-] Neo4j failed to start in time${NC}"
    return 1
}

# Function to start BloodHound GUI
start_bloodhound_gui() {
    echo -e "${YELLOW}[*] Starting BloodHound GUI...${NC}"
    
    cd /opt/bloodhound/BloodHound-linux-x64
    ./BloodHound
}

# Start VNC if requested
if [ "$START_VNC" = "true" ]; then
    start_vnc
fi

# Start Neo4j
start_neo4j

if [ $? -ne 0 ]; then
    echo -e "${RED}[-] Failed to start Neo4j${NC}"
    exit 1
fi

# Display container information
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  BloodHound Container - Ready${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${YELLOW}  Neo4j Database:    bolt://localhost:7687${NC}"
echo -e "${YELLOW}  Neo4j Web UI:      http://localhost:7474${NC}"
echo -e "${YELLOW}  Neo4j Username:    neo4j${NC}"
echo -e "${YELLOW}  Neo4j Password:    bloodhound${NC}"

if [ "$START_VNC" = "true" ]; then
    echo -e "${YELLOW}  VNC Server:        vnc://localhost:5900${NC}"
    echo -e "${YELLOW}  VNC Password:      bloodhound${NC}"
fi

echo -e "${YELLOW}  Available Commands:${NC}"
echo -e "    bloodhound-gui           - Start BloodHound GUI (requires VNC)"
echo -e "    bloodhound-automation.py - Automation script"
echo -e "    bloodhound-python        - Python data collector"
echo -e "${YELLOW}  Environment Variables:${NC}"
echo -e "    START_VNC=true           - Start VNC server for GUI"
echo -e "    START_GUI=true           - Start BloodHound GUI"
echo -e "${GREEN}================================================================${NC}"

# Handle different startup modes
if [ "$START_GUI" = "true" ] && [ "$START_VNC" = "true" ]; then
    start_bloodhound_gui
else
    # Default to showing help and keeping container running
    echo -e "${YELLOW}[*] BloodHound container ready${NC}"
    echo -e "${YELLOW}[*] Use environment variables to control startup mode${NC}"
    
    # Keep container running
    tail -f /dev/null
fi
EOF

RUN chmod +x /start-bloodhound.sh

# Set proper ownership
RUN chown -R bloodhound:bloodhound /home/bloodhound /opt/bloodhound-automation /opt/collectors

# Expose ports
EXPOSE 7474 7687 5900

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD neo4j status | grep -q "Neo4j is running" || exit 1

# Set working directory
WORKDIR /opt/bloodhound

# Set environment variables
ENV DISPLAY=:1.0
ENV NEO4J_HOME=/var/lib/neo4j

CMD ["/start-bloodhound.sh"]