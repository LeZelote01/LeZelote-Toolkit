# Kali Linux Tools Container
# Pentest-USB Toolkit - Docker Configuration
# Version: 1.0.0

FROM kalilinux/kali-rolling

LABEL maintainer="Pentest-USB Team"
LABEL description="Kali Linux Tools for Pentest-USB Toolkit"
LABEL version="1.0.0"

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install essential packages
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    vim \
    nano \
    tmux \
    screen \
    net-tools \
    netcat-traditional \
    dnsutils \
    iputils-ping \
    traceroute \
    whois \
    openssh-client \
    smbclient \
    ftp \
    telnet \
    nfs-common \
    && rm -rf /var/lib/apt/lists/*

# Install Kali meta-packages for comprehensive tool collection
RUN apt-get update && apt-get install -y \
    kali-tools-top10 \
    kali-tools-web \
    kali-tools-database \
    kali-tools-passwords \
    kali-tools-wireless \
    kali-tools-reverse-engineering \
    kali-tools-exploitation \
    kali-tools-social-engineering \
    kali-tools-sniffing-spoofing \
    kali-tools-post-exploitation \
    kali-tools-reporting \
    && rm -rf /var/lib/apt/lists/*

# Install additional essential tools not in meta-packages
RUN apt-get update && apt-get install -y \
    nmap \
    masscan \
    rustscan \
    gobuster \
    dirb \
    dirbuster \
    wfuzz \
    ffuf \
    sqlmap \
    nikto \
    whatweb \
    wafw00f \
    skipfish \
    uniscan \
    xsser \
    commix \
    wpscan \
    joomscan \
    droopescan \
    dnsrecon \
    dnsmap \
    fierce \
    sublist3r \
    amass \
    theharvester \
    recon-ng \
    maltego \
    shodan \
    dmitry \
    enum4linux \
    smbmap \
    nbtscan \
    onesixtyone \
    snmp-mibs-downloader \
    ike-scan \
    sslyze \
    sslscan \
    testssl.sh \
    hydra \
    medusa \
    ncrack \
    patator \
    john \
    hashcat \
    hashid \
    hash-identifier \
    samdump2 \
    mimikatz \
    powersploit \
    empire \
    metasploit-framework \
    armitage \
    beef-xss \
    set \
    king-phisher \
    gophish \
    responder \
    impacket-scripts \
    bloodhound \
    neo4j \
    crackmapexec \
    evil-winrm \
    chisel \
    proxychains4 \
    socat \
    netcat-openbsd \
    pwncat \
    rlwrap \
    seclists \
    rockyou \
    wordlists \
    cewl \
    crunch \
    cupp \
    rsmangler \
    maskprocessor \
    statsprocessor \
    princeprocessor \
    aircrack-ng \
    kismet \
    wifite \
    reaver \
    bully \
    hostapd-wpe \
    eapmd5pass \
    asleap \
    cowpatty \
    pyrit \
    && rm -rf /var/lib/apt/lists/*

# Install additional reverse engineering and forensics tools
RUN apt-get update && apt-get install -y \
    binwalk \
    foremost \
    steghide \
    stegosuite \
    outguess \
    exiftool \
    hexedit \
    ghex \
    bless \
    okteta \
    radare2 \
    gdb \
    gdb-multiarch \
    ltrace \
    strace \
    objdump \
    readelf \
    strings \
    file \
    volatility3 \
    autopsy \
    sleuthkit \
    dc3dd \
    dcfldd \
    && rm -rf /var/lib/apt/lists/*

# Copy installation script
COPY install-tools.sh /install-tools.sh
RUN chmod +x /install-tools.sh

# Run the installation script
RUN /install-tools.sh

# Create kali user for security
RUN useradd -m -s /bin/bash kali && \
    echo "kali:kali" | chpasswd && \
    usermod -aG sudo kali

# Create necessary directories
RUN mkdir -p \
    /home/kali/tools \
    /home/kali/wordlists \
    /home/kali/scripts \
    /home/kali/projects \
    /home/kali/reports \
    /opt/pentest-usb

# Install Python dependencies for automation
RUN pip3 install \
    requests \
    urllib3 \
    beautifulsoup4 \
    lxml \
    pycryptodome \
    paramiko \
    impacket \
    ldap3 \
    dnspython \
    scapy \
    netfilterqueue \
    netifaces \
    psutil \
    colorama \
    termcolor

# Create automation and utility scripts
RUN mkdir -p /opt/pentest-usb/scripts

# Create a comprehensive tool launcher script
RUN cat > /opt/pentest-usb/scripts/tool-launcher.py << 'EOF'
#!/usr/bin/env python3
"""
Kali Tools Launcher
Pentest-USB Toolkit Integration
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

class KaliToolsLauncher:
    def __init__(self):
        self.tools = {
            'reconnaissance': {
                'nmap': 'nmap',
                'masscan': 'masscan',
                'rustscan': 'rustscan',
                'gobuster': 'gobuster',
                'dirb': 'dirb',
                'ffuf': 'ffuf',
                'sublist3r': 'sublist3r',
                'amass': 'amass',
                'theharvester': 'theHarvester',
                'recon-ng': 'recon-ng',
                'dnsrecon': 'dnsrecon',
                'fierce': 'fierce'
            },
            'web': {
                'sqlmap': 'sqlmap',
                'nikto': 'nikto',
                'whatweb': 'whatweb',
                'wpscan': 'wpscan',
                'dirb': 'dirb',
                'gobuster': 'gobuster',
                'ffuf': 'ffuf',
                'wfuzz': 'wfuzz',
                'commix': 'commix',
                'xsser': 'xsser'
            },
            'exploitation': {
                'metasploit': 'msfconsole',
                'searchsploit': 'searchsploit',
                'sqlmap': 'sqlmap',
                'hydra': 'hydra',
                'john': 'john',
                'hashcat': 'hashcat',
                'crackmapexec': 'crackmapexec',
                'evil-winrm': 'evil-winrm',
                'responder': 'responder'
            },
            'wireless': {
                'aircrack-ng': 'aircrack-ng',
                'kismet': 'kismet',
                'wifite': 'wifite',
                'reaver': 'reaver',
                'bully': 'bully'
            },
            'forensics': {
                'volatility': 'vol.py',
                'autopsy': 'autopsy',
                'binwalk': 'binwalk',
                'foremost': 'foremost',
                'steghide': 'steghide',
                'exiftool': 'exiftool'
            }
        }
    
    def list_categories(self):
        """List available tool categories"""
        print("Available tool categories:")
        for category in self.tools.keys():
            print(f"  - {category}")
    
    def list_tools(self, category=None):
        """List tools in a category or all tools"""
        if category:
            if category in self.tools:
                print(f"Tools in {category} category:")
                for tool, command in self.tools[category].items():
                    print(f"  - {tool} ({command})")
            else:
                print(f"Unknown category: {category}")
                self.list_categories()
        else:
            print("All available tools:")
            for category, tools in self.tools.items():
                print(f"\n{category.upper()}:")
                for tool, command in tools.items():
                    print(f"  - {tool} ({command})")
    
    def run_tool(self, tool_name, args=None):
        """Run a specific tool"""
        command = None
        category = None
        
        # Find the tool in categories
        for cat, tools in self.tools.items():
            if tool_name in tools:
                command = tools[tool_name]
                category = cat
                break
        
        if not command:
            print(f"Tool '{tool_name}' not found")
            return False
        
        print(f"Running {tool_name} from {category} category...")
        
        # Build command
        if args:
            full_command = [command] + args
        else:
            full_command = [command, '--help']
        
        try:
            result = subprocess.run(full_command, check=False)
            return result.returncode == 0
        except FileNotFoundError:
            print(f"Tool '{command}' not found on system")
            return False
        except Exception as e:
            print(f"Error running tool: {e}")
            return False
    
    def run_quick_scan(self, target, scan_type='basic'):
        """Run a quick scan with multiple tools"""
        print(f"Running {scan_type} scan on {target}")
        
        if scan_type == 'basic':
            tools_to_run = [
                ('nmap', ['-sS', '-sV', target]),
                ('whatweb', [target]),
                ('nikto', ['-h', target])
            ]
        elif scan_type == 'web':
            tools_to_run = [
                ('nmap', ['-sS', '-p80,443,8080,8443', target]),
                ('whatweb', [target]),
                ('nikto', ['-h', target]),
                ('dirb', [f'http://{target}'])
            ]
        elif scan_type == 'network':
            tools_to_run = [
                ('nmap', ['-sS', '-sV', '-O', target]),
                ('enum4linux', [target])
            ]
        else:
            print(f"Unknown scan type: {scan_type}")
            return False
        
        results = {}
        
        for tool, args in tools_to_run:
            print(f"\n[+] Running {tool} with args: {' '.join(args)}")
            
            try:
                result = subprocess.run([tool] + args, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=300)
                
                results[tool] = {
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
                if result.returncode == 0:
                    print(f"[+] {tool} completed successfully")
                else:
                    print(f"[-] {tool} failed with return code {result.returncode}")
                    
            except subprocess.TimeoutExpired:
                print(f"[-] {tool} timed out")
                results[tool] = {'error': 'timeout'}
            except FileNotFoundError:
                print(f"[-] {tool} not found")
                results[tool] = {'error': 'not_found'}
            except Exception as e:
                print(f"[-] Error running {tool}: {e}")
                results[tool] = {'error': str(e)}
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Kali Tools Launcher for Pentest-USB')
    
    parser.add_argument('command', 
                       choices=['list', 'run', 'scan'],
                       help='Command to execute')
    
    parser.add_argument('--category', help='Tool category')
    parser.add_argument('--tool', help='Specific tool to run')
    parser.add_argument('--target', help='Target for scanning')
    parser.add_argument('--type', choices=['basic', 'web', 'network'], 
                       default='basic', help='Scan type')
    parser.add_argument('--args', nargs='*', help='Arguments to pass to tool')
    
    args = parser.parse_args()
    
    launcher = KaliToolsLauncher()
    
    try:
        if args.command == 'list':
            if args.category:
                launcher.list_tools(args.category)
            else:
                launcher.list_categories()
                
        elif args.command == 'run':
            if not args.tool:
                print("Error: --tool required for run command")
                sys.exit(1)
            
            launcher.run_tool(args.tool, args.args)
            
        elif args.command == 'scan':
            if not args.target:
                print("Error: --target required for scan command")
                sys.exit(1)
            
            results = launcher.run_quick_scan(args.target, args.type)
            
            print(f"\n[+] Scan of {args.target} completed")
            print(f"[+] Results summary:")
            
            for tool, result in results.items():
                if 'error' in result:
                    print(f"  {tool}: ERROR ({result['error']})")
                else:
                    status = "SUCCESS" if result['returncode'] == 0 else "FAILED"
                    print(f"  {tool}: {status}")
                    
    except KeyboardInterrupt:
        print("\n[!] Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

RUN chmod +x /opt/pentest-usb/scripts/tool-launcher.py

# Create environment setup script
RUN cat > /opt/pentest-usb/scripts/setup-environment.sh << 'EOF'
#!/bin/bash
# Environment Setup Script for Kali Tools Container
# Pentest-USB Toolkit Integration

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[+] Setting up Kali Tools environment...${NC}"

# Update locate database
echo -e "${YELLOW}[*] Updating locate database...${NC}"
updatedb

# Update Metasploit database
echo -e "${YELLOW}[*] Initializing Metasploit database...${NC}"
msfdb init

# Download and update wordlists
echo -e "${YELLOW}[*] Setting up wordlists...${NC}"
if [ ! -f /usr/share/wordlists/rockyou.txt ]; then
    gzip -d /usr/share/wordlists/rockyou.txt.gz 2>/dev/null || true
fi

# Setup SecLists if not present
if [ ! -d /usr/share/seclists ]; then
    echo -e "${YELLOW}[*] Installing SecLists...${NC}"
    git clone https://github.com/danielmiessler/SecLists.git /usr/share/seclists
fi

# Update searchsploit database
echo -e "${YELLOW}[*] Updating searchsploit database...${NC}"
searchsploit -u

# Create useful aliases
echo -e "${YELLOW}[*] Setting up aliases...${NC}"
cat >> /home/kali/.bashrc << 'BASHEOF'

# Pentest-USB Toolkit aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Tool shortcuts
alias nse='ls /usr/share/nmap/scripts/ | grep'
alias searchsploit='searchsploit --color'
alias msfconsole='msfconsole -q'
alias metasploit='msfconsole -q'

# Pentest-USB specific
alias pentool='/opt/pentest-usb/scripts/tool-launcher.py'
alias quickscan='/opt/pentest-usb/scripts/tool-launcher.py scan --type basic --target'
alias webscan='/opt/pentest-usb/scripts/tool-launcher.py scan --type web --target'
alias netscan='/opt/pentest-usb/scripts/tool-launcher.py scan --type network --target'

BASHEOF

echo -e "${GREEN}[+] Environment setup completed!${NC}"
EOF

RUN chmod +x /opt/pentest-usb/scripts/setup-environment.sh

# Create startup script
RUN cat > /start-kali.sh << 'EOF'
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Kali Linux Tools Container${NC}"
echo -e "${GREEN}  Pentest-USB Toolkit Integration${NC}"
echo -e "${GREEN}================================================================${NC}"

# Run environment setup if not done before
if [ ! -f /home/kali/.setup_complete ]; then
    echo -e "${YELLOW}[*] Running first-time setup...${NC}"
    /opt/pentest-usb/scripts/setup-environment.sh
    touch /home/kali/.setup_complete
fi

# Display information
echo -e "${YELLOW}  Available Tools:${NC}"
echo -e "    Reconnaissance: nmap, masscan, gobuster, sublist3r, amass"
echo -e "    Web Testing: sqlmap, nikto, wpscan, dirb, ffuf"
echo -e "    Exploitation: metasploit, hydra, john, hashcat"
echo -e "    Wireless: aircrack-ng, kismet, wifite"
echo -e "    Forensics: volatility, binwalk, steghide"
echo -e ""
echo -e "${YELLOW}  Quick Commands:${NC}"
echo -e "    pentool list                    - List available tools"
echo -e "    pentool run --tool nmap         - Run specific tool"
echo -e "    quickscan <target>              - Quick network scan"
echo -e "    webscan <target>                - Web application scan"
echo -e "    netscan <target>                - Network enumeration"
echo -e ""
echo -e "${YELLOW}  Key Directories:${NC}"
echo -e "    /usr/share/wordlists/           - Password wordlists"
echo -e "    /usr/share/seclists/            - SecLists collection"
echo -e "    /usr/share/nmap/scripts/        - Nmap scripts"
echo -e "    /home/kali/tools/               - Custom tools"
echo -e "    /home/kali/projects/            - Project workspace"
echo -e "${GREEN}================================================================${NC}"

# Switch to kali user and start bash
exec sudo -u kali bash
EOF

RUN chmod +x /start-kali.sh

# Set proper ownership
RUN chown -R kali:kali /home/kali /opt/pentest-usb

# Install additional custom tools and configurations
RUN apt-get update && apt-get install -y \
    zsh \
    oh-my-zsh \
    && rm -rf /var/lib/apt/lists/*

# Expose common ports for services
EXPOSE 80 443 4444 8080 8443

# Set working directory
WORKDIR /home/kali

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD which nmap && which sqlmap && which metasploit || exit 1

# Set environment variables
ENV PATH="/opt/pentest-usb/scripts:${PATH}"
ENV HOME="/home/kali"

CMD ["/start-kali.sh"]