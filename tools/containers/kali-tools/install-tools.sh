#!/bin/bash
# Kali Tools Installation Script
# Pentest-USB Toolkit - Docker Configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Kali Tools Installation Script${NC}"
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

# Update package lists
log "Updating package lists..."
apt-get update

# Install additional tools not in standard Kali repos
log "Installing additional security tools..."

# Install Go (required for some tools)
if ! command -v go &> /dev/null; then
    log "Installing Go programming language..."
    wget -q https://golang.org/dl/go1.21.0.linux-amd64.tar.gz -O /tmp/go.tar.gz
    tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile
    export PATH=$PATH:/usr/local/go/bin
    success "Go installed successfully"
fi

# Install additional reconnaissance tools
log "Installing additional reconnaissance tools..."

# Install subfinder
if ! command -v subfinder &> /dev/null; then
    log "Installing subfinder..."
    GO111MODULE=on /usr/local/go/bin/go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    mv /root/go/bin/subfinder /usr/local/bin/
fi

# Install httpx
if ! command -v httpx &> /dev/null; then
    log "Installing httpx..."
    GO111MODULE=on /usr/local/go/bin/go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    mv /root/go/bin/httpx /usr/local/bin/
fi

# Install nuclei
if ! command -v nuclei &> /dev/null; then
    log "Installing nuclei..."
    GO111MODULE=on /usr/local/go/bin/go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
    mv /root/go/bin/nuclei /usr/local/bin/
fi

# Install katana
if ! command -v katana &> /dev/null; then
    log "Installing katana..."
    GO111MODULE=on /usr/local/go/bin/go install github.com/projectdiscovery/katana/cmd/katana@latest
    mv /root/go/bin/katana /usr/local/bin/
fi

# Install additional web tools
log "Installing additional web application tools..."

# Install Arjun (HTTP parameter discovery)
pip3 install arjun

# Install XSStrike
if [ ! -d "/opt/XSStrike" ]; then
    log "Installing XSStrike..."
    git clone https://github.com/s0md3v/XSStrike.git /opt/XSStrike
    chmod +x /opt/XSStrike/xsstrike.py
    ln -sf /opt/XSStrike/xsstrike.py /usr/local/bin/xsstrike
fi

# Install Corsy (CORS misconfiguration scanner)
if [ ! -d "/opt/Corsy" ]; then
    log "Installing Corsy..."
    git clone https://github.com/s0md3v/Corsy.git /opt/Corsy
    pip3 install -r /opt/Corsy/requirements.txt
    chmod +x /opt/Corsy/corsy.py
    ln -sf /opt/Corsy/corsy.py /usr/local/bin/corsy
fi

# Install JSFScan (JavaScript file scanner)
if [ ! -d "/opt/JSFScan" ]; then
    log "Installing JSFScan..."
    git clone https://github.com/KathanP19/JSFScan.sh.git /opt/JSFScan
    chmod +x /opt/JSFScan/JSFScan.sh
    ln -sf /opt/JSFScan/JSFScan.sh /usr/local/bin/jsfscan
fi

# Install additional network tools
log "Installing additional network tools..."

# Install Impacket (if not already installed)
if ! python3 -c "import impacket" &> /dev/null; then
    log "Installing Impacket..."
    pip3 install impacket
fi

# Install ldapdomaindump
pip3 install ldapdomaindump

# Install bloodhound-python
pip3 install bloodhound

# Install crackmapexec (if not available)
if ! command -v crackmapexec &> /dev/null; then
    log "Installing CrackMapExec..."
    pip3 install crackmapexec
fi

# Install additional password tools
log "Installing additional password cracking tools..."

# Install hashcat rules
if [ ! -d "/usr/share/hashcat/rules" ]; then
    mkdir -p /usr/share/hashcat/rules
fi

# Download best64.rule if not exists
if [ ! -f "/usr/share/hashcat/rules/best64.rule" ]; then
    log "Downloading best64.rule..."
    wget -q https://raw.githubusercontent.com/hashcat/hashcat/master/rules/best64.rule -O /usr/share/hashcat/rules/best64.rule
fi

# Install additional wordlists
log "Setting up additional wordlists..."

# Ensure wordlists directory exists
mkdir -p /usr/share/wordlists

# Download additional wordlists
if [ ! -f "/usr/share/wordlists/common.txt" ]; then
    log "Downloading common.txt wordlist..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O /usr/share/wordlists/common.txt
fi

if [ ! -f "/usr/share/wordlists/directory-list-2.3-medium.txt" ]; then
    log "Downloading directory-list-2.3-medium.txt..."
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt -O /usr/share/wordlists/directory-list-2.3-medium.txt
fi

# Install additional wireless tools
log "Installing additional wireless tools..."

# Install Airgeddon (if not present)
if [ ! -d "/opt/airgeddon" ]; then
    log "Installing Airgeddon..."
    git clone https://github.com/v1s1t0r1sh3r3/airgeddon.git /opt/airgeddon
    chmod +x /opt/airgeddon/airgeddon.sh
    ln -sf /opt/airgeddon/airgeddon.sh /usr/local/bin/airgeddon
fi

# Install Wifiphisher (if not present)
if ! command -v wifiphisher &> /dev/null; then
    log "Installing Wifiphisher..."
    pip3 install wifiphisher
fi

# Install additional exploitation tools
log "Installing additional exploitation tools..."

# Install pwntools
pip3 install pwntools

# Install ropper (ROP gadget finder)
pip3 install ropper

# Install one_gadget (for libc exploitation)
if ! command -v one_gadget &> /dev/null; then
    log "Installing one_gadget..."
    gem install one_gadget
fi

# Install additional post-exploitation tools
log "Installing additional post-exploitation tools..."

# Install PowerSploit
if [ ! -d "/opt/PowerSploit" ]; then
    log "Installing PowerSploit..."
    git clone https://github.com/PowerShellMafia/PowerSploit.git /opt/PowerSploit
fi

# Install LinEnum
if [ ! -f "/opt/LinEnum.sh" ]; then
    log "Installing LinEnum..."
    wget -q https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh -O /opt/LinEnum.sh
    chmod +x /opt/LinEnum.sh
fi

# Install winPEAS
if [ ! -f "/opt/winPEAS.exe" ]; then
    log "Installing winPEAS..."
    wget -q https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEAS.exe -O /opt/winPEAS.exe
fi

# Install linPEAS
if [ ! -f "/opt/linpeas.sh" ]; then
    log "Installing linPEAS..."
    wget -q https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -O /opt/linpeas.sh
    chmod +x /opt/linpeas.sh
fi

# Install GTFOBins lookup tool
if [ ! -d "/opt/gtfoblookup" ]; then
    log "Installing GTFOBins lookup..."
    git clone https://github.com/nccgroup/GTFOBins.github.io.git /opt/gtfoblookup
fi

# Install additional forensics tools
log "Installing additional forensics tools..."

# Install volatility3 profiles
if [ -d "/usr/lib/python3/dist-packages/volatility3" ]; then
    log "Setting up Volatility3 profiles..."
    mkdir -p /usr/lib/python3/dist-packages/volatility3/symbols
fi

# Install YARA
if ! command -v yara &> /dev/null; then
    log "Installing YARA..."
    apt-get install -y yara
fi

# Install ClamAV for malware scanning
if ! command -v clamscan &> /dev/null; then
    log "Installing ClamAV..."
    apt-get install -y clamav clamav-daemon
    freshclam
fi

# Install additional reverse engineering tools
log "Installing additional reverse engineering tools..."

# Install Ghidra (if not present)
if [ ! -d "/opt/ghidra" ]; then
    log "Downloading Ghidra..."
    GHIDRA_VERSION="10.3.3_PUBLIC"
    wget -q "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_LINUX.zip" -O /tmp/ghidra.zip
    unzip -q /tmp/ghidra.zip -d /opt/
    mv /opt/ghidra_* /opt/ghidra
    rm /tmp/ghidra.zip
    ln -sf /opt/ghidra/ghidraRun /usr/local/bin/ghidra
fi

# Install IDA Free (demo version)
# Note: This would require manual download and license agreement

# Install additional mobile testing tools
log "Installing additional mobile testing tools..."

# Install APKTool
if ! command -v apktool &> /dev/null; then
    log "Installing APKTool..."
    wget -q https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool
    wget -q https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar -O /usr/local/bin/apktool.jar
    chmod +x /usr/local/bin/apktool
fi

# Install dex2jar
if [ ! -d "/opt/dex2jar" ]; then
    log "Installing dex2jar..."
    wget -q https://github.com/pxb1988/dex2jar/releases/download/v2.4/dex2jar-2.4.zip -O /tmp/dex2jar.zip
    unzip -q /tmp/dex2jar.zip -d /opt/
    mv /opt/dex2jar-* /opt/dex2jar
    rm /tmp/dex2jar.zip
    chmod +x /opt/dex2jar/*.sh
    for script in /opt/dex2jar/*.sh; do
        ln -sf "$script" "/usr/local/bin/$(basename "$script" .sh)"
    done
fi

# Install JADX (Java Decompiler)
if [ ! -d "/opt/jadx" ]; then
    log "Installing JADX..."
    wget -q https://github.com/skylot/jadx/releases/latest/download/jadx-1.4.7.zip -O /tmp/jadx.zip
    unzip -q /tmp/jadx.zip -d /opt/jadx
    rm /tmp/jadx.zip
    chmod +x /opt/jadx/bin/jadx*
    ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx
    ln -sf /opt/jadx/bin/jadx-gui /usr/local/bin/jadx-gui
fi

# Clean up
log "Cleaning up..."
apt-get autoremove -y
apt-get autoclean
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/*

# Update file permissions
log "Setting proper permissions..."
chmod -R 755 /opt/
chown -R root:root /opt/

# Create symlinks for commonly used tools
log "Creating tool symlinks..."
mkdir -p /usr/local/bin

# Ensure all installed tools are in PATH
if [ -d "/root/go/bin" ]; then
    cp /root/go/bin/* /usr/local/bin/ 2>/dev/null || true
fi

# Update locate database
log "Updating locate database..."
updatedb

success "All additional tools installed successfully!"

# Display installation summary
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Installation Summary${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${YELLOW}  Reconnaissance Tools:${NC} subfinder, httpx, nuclei, katana"
echo -e "${YELLOW}  Web Application Tools:${NC} XSStrike, Corsy, JSFScan, Arjun"
echo -e "${YELLOW}  Network Tools:${NC} Impacket, BloodHound, CrackMapExec"
echo -e "${YELLOW}  Password Tools:${NC} hashcat rules, additional wordlists"
echo -e "${YELLOW}  Wireless Tools:${NC} Airgeddon, Wifiphisher"
echo -e "${YELLOW}  Exploitation Tools:${NC} pwntools, ropper, one_gadget"
echo -e "${YELLOW}  Post-Exploitation:${NC} PowerSploit, LinEnum, winPEAS, linPEAS"
echo -e "${YELLOW}  Forensics Tools:${NC} YARA, ClamAV, Volatility3 setup"
echo -e "${YELLOW}  Reverse Engineering:${NC} Ghidra, radare2"
echo -e "${YELLOW}  Mobile Testing:${NC} APKTool, dex2jar, JADX"
echo -e "${GREEN}================================================================${NC}"

log "Installation script completed successfully!"