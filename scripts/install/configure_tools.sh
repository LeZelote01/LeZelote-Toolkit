#!/bin/bash
# =============================================================================
# LeZelote-Toolkit - Tools Configuration Script
# =============================================================================
# Description: Configure and verify security tools installation
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly LOG_FILE="$PROJECT_ROOT/logs/tools_configuration.log"
readonly CONFIG_DIR="$PROJECT_ROOT/config"
readonly TOOLS_DIR="$PROJECT_ROOT/tools"
readonly BINARIES_DIR="$TOOLS_DIR/binaries"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case "$level" in
        "INFO")  echo -e "${BLUE}[INFO]${NC} $message" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
    esac
}

print_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LeZelote-Toolkit Tools Configuration                      ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            echo "ubuntu"
        elif command -v yum >/dev/null 2>&1; then
            echo "centos"
        elif command -v pacman >/dev/null 2>&1; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

get_binary_extension() {
    local os="$1"
    if [[ "$os" == "windows" ]]; then
        echo ".exe"
    else
        echo ""
    fi
}

# =============================================================================
# Configuration Functions
# =============================================================================

create_tool_directories() {
    log "INFO" "Creating tool directories..."
    
    local os=$(detect_os)
    local directories=(
        "$BINARIES_DIR/$os"
        "$TOOLS_DIR/python_scripts"
        "$TOOLS_DIR/containers"
        "$PROJECT_ROOT/data/wordlists/passwords"
        "$PROJECT_ROOT/data/wordlists/directories"
        "$PROJECT_ROOT/data/wordlists/dns"
        "$PROJECT_ROOT/outputs/scans"
        "$PROJECT_ROOT/outputs/reports"
        "$PROJECT_ROOT/outputs/temporary"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log "INFO" "Created directory: $dir"
        fi
    done
    
    log "SUCCESS" "Tool directories created successfully"
}

configure_nmap() {
    log "INFO" "Configuring Nmap..."
    
    # Check if nmap is installed
    if command -v nmap >/dev/null 2>&1; then
        local nmap_version=$(nmap --version | head -n1)
        log "INFO" "Found Nmap: $nmap_version"
        
        # Create nmap configuration
        local nmap_config="$CONFIG_DIR/nmap_config.yaml"
        cat > "$nmap_config" << 'EOF'
nmap:
  default_options: "-sS -O -sV -sC --version-all"
  timing_template: "T4"
  max_rate: "1000"
  scripts_directory: "/usr/share/nmap/scripts"
  output_formats: ["xml", "normal", "grepable"]
  
profiles:
  quick:
    options: "-sS -T4 --top-ports 1000"
    description: "Quick TCP SYN scan of top 1000 ports"
  
  comprehensive:
    options: "-sS -sU -O -sV -sC -A --script vuln -T4"
    description: "Comprehensive scan with OS detection and vulnerability scripts"
  
  stealth:
    options: "-sS -f -T2 -D RND:10"
    description: "Stealth scan with fragmentation and decoys"
EOF
        
        log "SUCCESS" "Nmap configured successfully"
    else
        log "WARN" "Nmap not found, skipping configuration"
    fi
}

configure_metasploit() {
    log "INFO" "Configuring Metasploit..."
    
    # Check if Metasploit is installed
    if command -v msfconsole >/dev/null 2>&1; then
        log "INFO" "Found Metasploit Framework"
        
        # Initialize Metasploit database if not already done
        if command -v msfdb >/dev/null 2>&1; then
            if ! msfdb status | grep -q "postgresql selected"; then
                log "INFO" "Initializing Metasploit database..."
                msfdb init || log "WARN" "Failed to initialize Metasploit database"
            else
                log "INFO" "Metasploit database already initialized"
            fi
        fi
        
        # Create Metasploit configuration
        local msf_config="$CONFIG_DIR/metasploit_config.yaml"
        cat > "$msf_config" << 'EOF'
metasploit:
  console_path: "msfconsole"
  database_enabled: true
  auto_update: true
  
modules:
  exploit:
    default_payload: "generic/shell_reverse_tcp"
    verify_ssl: false
  
  auxiliary:
    threads: 10
    verbose: false
  
  post:
    migrate: true
    cleanup: true
EOF
        
        log "SUCCESS" "Metasploit configured successfully"
    else
        log "WARN" "Metasploit not found, skipping configuration"
    fi
}

configure_burpsuite() {
    log "INFO" "Configuring Burp Suite..."
    
    local burp_config="$CONFIG_DIR/burpsuite_config.yaml"
    cat > "$burp_config" << 'EOF'
burpsuite:
  executable_path: ""  # Will be auto-detected
  project_path: "${PROJECT_ROOT}/data/burp_projects"
  
proxy:
  listen_address: "127.0.0.1"
  listen_port: 8080
  intercept_enabled: false
  
scanner:
  crawl_optimization: "thorough"
  audit_optimization: "fast"
  
extensions:
  - name: "Logger++"
    enabled: true
  - name: "Autorize"
    enabled: true
  - name: "Software Vulnerability Scanner"
    enabled: true
EOF
    
    # Create Burp projects directory
    mkdir -p "$PROJECT_ROOT/data/burp_projects"
    
    log "SUCCESS" "Burp Suite configuration created"
}

configure_sqlmap() {
    log "INFO" "Configuring SQLMap..."
    
    if command -v sqlmap >/dev/null 2>&1; then
        local sqlmap_version=$(sqlmap --version 2>/dev/null | head -n1)
        log "INFO" "Found SQLMap: $sqlmap_version"
        
        local sqlmap_config="$CONFIG_DIR/sqlmap_config.yaml"
        cat > "$sqlmap_config" << 'EOF'
sqlmap:
  default_options: "--batch --random-agent"
  risk_level: 1
  verbosity_level: 1
  
techniques:
  - "B"  # Boolean-based blind
  - "E"  # Error-based
  - "U"  # Union query-based
  - "S"  # Stacked queries
  - "T"  # Time-based blind

profiles:
  quick:
    options: "--batch --random-agent --level=1 --risk=1"
    description: "Quick SQL injection test"
  
  comprehensive:
    options: "--batch --random-agent --level=5 --risk=3 --tamper=space2comment"
    description: "Comprehensive SQL injection test with evasion"
EOF
        
        log "SUCCESS" "SQLMap configured successfully"
    else
        log "WARN" "SQLMap not found, skipping configuration"
    fi
}

configure_nikto() {
    log "INFO" "Configuring Nikto..."
    
    if command -v nikto >/dev/null 2>&1; then
        log "INFO" "Found Nikto"
        
        local nikto_config="$CONFIG_DIR/nikto_config.yaml"
        cat > "$nikto_config" << 'EOF'
nikto:
  default_options: "-ask no -ssl"
  max_time: "1800"  # 30 minutes
  
plugins:
  - "apache_expect_xss"
  - "auth"
  - "cgi"
  - "content_search"
  - "cookies"
  - "headers"
  
profiles:
  quick:
    options: "-ask no -Tuning 1,2,3"
    description: "Quick web vulnerability scan"
  
  comprehensive:
    options: "-ask no -Tuning 0"
    description: "Comprehensive web vulnerability scan"
EOF
        
        log "SUCCESS" "Nikto configured successfully"
    else
        log "WARN" "Nikto not found, skipping configuration"
    fi
}

configure_aircrack_ng() {
    log "INFO" "Configuring Aircrack-ng..."
    
    if command -v aircrack-ng >/dev/null 2>&1; then
        local aircrack_version=$(aircrack-ng --version 2>&1 | head -n1)
        log "INFO" "Found Aircrack-ng: $aircrack_version"
        
        local aircrack_config="$CONFIG_DIR/aircrack_config.yaml"
        cat > "$aircrack_config" << 'EOF'
aircrack:
  interface: ""  # Will be auto-detected
  wordlist: "${PROJECT_ROOT}/data/wordlists/passwords/rockyou.txt"
  
capture:
  channel_hopping: true
  capture_beacons: true
  capture_ivs: true
  
attack:
  deauth_count: 10
  replay_count: 500
  
tools:
  airodump_options: "-w capture --output-format pcap"
  aireplay_options: "--deauth 10"
  aircrack_options: "-a 2"
EOF
        
        log "SUCCESS" "Aircrack-ng configured successfully"
    else
        log "WARN" "Aircrack-ng not found, skipping configuration"
    fi
}

configure_john_the_ripper() {
    log "INFO" "Configuring John the Ripper..."
    
    if command -v john >/dev/null 2>&1; then
        local john_version=$(john --version 2>&1 | head -n1)
        log "INFO" "Found John the Ripper: $john_version"
        
        local john_config="$CONFIG_DIR/john_config.yaml"
        cat > "$john_config" << 'EOF'
john:
  wordlist: "${PROJECT_ROOT}/data/wordlists/passwords/rockyou.txt"
  rules: "best64"
  
formats:
  - "NT"
  - "md5crypt"
  - "sha512crypt"
  - "bcrypt"
  
profiles:
  quick:
    options: "--wordlist=${PROJECT_ROOT}/data/wordlists/passwords/top_100k.txt"
    description: "Quick dictionary attack"
  
  comprehensive:
    options: "--wordlist=${PROJECT_ROOT}/data/wordlists/passwords/rockyou.txt --rules=all"
    description: "Comprehensive attack with all rules"
EOF
        
        log "SUCCESS" "John the Ripper configured successfully"
    else
        log "WARN" "John the Ripper not found, skipping configuration"
    fi
}

configure_hashcat() {
    log "INFO" "Configuring Hashcat..."
    
    if command -v hashcat >/dev/null 2>&1; then
        local hashcat_version=$(hashcat --version 2>/dev/null | head -n1)
        log "INFO" "Found Hashcat: $hashcat_version"
        
        local hashcat_config="$CONFIG_DIR/hashcat_config.yaml"
        cat > "$hashcat_config" << 'EOF'
hashcat:
  workload_profile: 3  # High performance
  gpu_temp_limit: 90
  
attack_modes:
  dictionary: 0
  combinator: 1
  brute_force: 3
  hybrid_wordlist_mask: 6
  hybrid_mask_wordlist: 7
  
hash_types:
  ntlm: 1000
  md5: 0
  sha1: 100
  sha256: 1400
  bcrypt: 3200
  
profiles:
  quick:
    options: "-a 0 --force"
    wordlist: "${PROJECT_ROOT}/data/wordlists/passwords/top_100k.txt"
    description: "Quick dictionary attack"
  
  comprehensive:
    options: "-a 0 --force -r ${PROJECT_ROOT}/data/wordlists/rules/best64.rule"
    wordlist: "${PROJECT_ROOT}/data/wordlists/passwords/rockyou.txt"
    description: "Comprehensive attack with rules"
EOF
        
        log "SUCCESS" "Hashcat configured successfully"
    else
        log "WARN" "Hashcat not found, skipping configuration"
    fi
}

create_tool_wrappers() {
    log "INFO" "Creating tool wrapper scripts..."
    
    local wrappers_dir="$TOOLS_DIR/wrappers"
    mkdir -p "$wrappers_dir"
    
    # Create Nmap wrapper
    cat > "$wrappers_dir/nmap_wrapper.py" << 'EOF'
#!/usr/bin/env python3
"""
Nmap wrapper script for LeZelote-Toolkit
"""
import sys
import subprocess
import yaml
from pathlib import Path

def load_config():
    config_file = Path(__file__).parent.parent.parent / "config" / "nmap_config.yaml"
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def run_nmap(profile, target, additional_args=None):
    config = load_config()
    
    if profile in config['profiles']:
        options = config['profiles'][profile]['options']
    else:
        options = config['nmap']['default_options']
    
    cmd = ['nmap'] + options.split() + [target]
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: nmap_wrapper.py <profile> <target> [additional_args...]")
        sys.exit(1)
    
    profile = sys.argv[1]
    target = sys.argv[2]
    additional_args = sys.argv[3:] if len(sys.argv) > 3 else None
    
    result = run_nmap(profile, target, additional_args)
    sys.exit(result.returncode)
EOF
    
    chmod +x "$wrappers_dir/nmap_wrapper.py"
    
    # Create SQLMap wrapper
    cat > "$wrappers_dir/sqlmap_wrapper.py" << 'EOF'
#!/usr/bin/env python3
"""
SQLMap wrapper script for LeZelote-Toolkit
"""
import sys
import subprocess
import yaml
from pathlib import Path

def load_config():
    config_file = Path(__file__).parent.parent.parent / "config" / "sqlmap_config.yaml"
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def run_sqlmap(profile, url, additional_args=None):
    config = load_config()
    
    if profile in config['profiles']:
        options = config['profiles'][profile]['options']
    else:
        options = config['sqlmap']['default_options']
    
    cmd = ['sqlmap'] + options.split() + ['-u', url]
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: sqlmap_wrapper.py <profile> <url> [additional_args...]")
        sys.exit(1)
    
    profile = sys.argv[1]
    url = sys.argv[2]
    additional_args = sys.argv[3:] if len(sys.argv) > 3 else None
    
    result = run_sqlmap(profile, url, additional_args)
    sys.exit(result.returncode)
EOF
    
    chmod +x "$wrappers_dir/sqlmap_wrapper.py"
    
    log "SUCCESS" "Tool wrapper scripts created successfully"
}

verify_tool_configurations() {
    log "INFO" "Verifying tool configurations..."
    
    local config_files=(
        "nmap_config.yaml"
        "metasploit_config.yaml"
        "burpsuite_config.yaml"
        "sqlmap_config.yaml"
        "nikto_config.yaml"
        "aircrack_config.yaml"
        "john_config.yaml"
        "hashcat_config.yaml"
    )
    
    local verified=0
    local total=${#config_files[@]}
    
    for config_file in "${config_files[@]}"; do
        local config_path="$CONFIG_DIR/$config_file"
        if [[ -f "$config_path" ]]; then
            if python3 -c "import yaml; yaml.safe_load(open('$config_path', 'r'))" 2>/dev/null; then
                log "INFO" "✓ $config_file is valid"
                ((verified++))
            else
                log "ERROR" "✗ $config_file has invalid YAML syntax"
            fi
        else
            log "WARN" "✗ $config_file not found"
        fi
    done
    
    log "INFO" "Configuration verification: $verified/$total files valid"
    
    if [[ $verified -eq $total ]]; then
        log "SUCCESS" "All tool configurations verified successfully"
        return 0
    else
        log "WARN" "Some tool configurations are missing or invalid"
        return 1
    fi
}

create_tool_aliases() {
    log "INFO" "Creating tool aliases..."
    
    local aliases_file="$PROJECT_ROOT/.tool_aliases"
    cat > "$aliases_file" << EOF
# LeZelote-Toolkit Tool Aliases
alias lz-nmap='$TOOLS_DIR/wrappers/nmap_wrapper.py'
alias lz-sqlmap='$TOOLS_DIR/wrappers/sqlmap_wrapper.py'
alias lz-scan-quick='$TOOLS_DIR/wrappers/nmap_wrapper.py quick'
alias lz-scan-full='$TOOLS_DIR/wrappers/nmap_wrapper.py comprehensive'
alias lz-sql-test='$TOOLS_DIR/wrappers/sqlmap_wrapper.py quick'
EOF
    
    # Add to shell configuration
    local shell_configs=(
        "$HOME/.bashrc"
        "$HOME/.zshrc"
        "$HOME/.profile"
    )
    
    for shell_config in "${shell_configs[@]}"; do
        if [[ -f "$shell_config" ]]; then
            if ! grep -q "LeZelote-Toolkit Tool Aliases" "$shell_config"; then
                echo "" >> "$shell_config"
                echo "# Source LeZelote-Toolkit tool aliases" >> "$shell_config"
                echo "source $aliases_file" >> "$shell_config"
                log "INFO" "Added aliases to $shell_config"
            fi
        fi
    done
    
    log "SUCCESS" "Tool aliases created successfully"
}

# =============================================================================
# Main Configuration Process
# =============================================================================

main() {
    print_banner
    
    log "INFO" "Starting tools configuration..."
    log "INFO" "Project root: $PROJECT_ROOT"
    
    # Create tool directories
    create_tool_directories
    
    # Configure individual tools
    configure_nmap
    configure_metasploit
    configure_burpsuite
    configure_sqlmap
    configure_nikto
    configure_aircrack_ng
    configure_john_the_ripper
    configure_hashcat
    
    # Create tool wrappers
    create_tool_wrappers
    
    # Create tool aliases
    create_tool_aliases
    
    # Verify configurations
    if verify_tool_configurations; then
        log "SUCCESS" "Tools configuration completed successfully!"
    else
        log "WARN" "Tools configuration completed with some warnings"
    fi
    
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                        Tools Configuration Complete!                         ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC} Configuration files created in: $CONFIG_DIR"
    echo -e "${GREEN}║${NC} Tool wrappers created in: $TOOLS_DIR/wrappers"
    echo -e "${GREEN}║${NC} Tool aliases created in: $aliases_file"
    echo -e "${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} To use tool aliases, restart your terminal or run:"
    echo -e "${GREEN}║${NC}   source $aliases_file"
    echo -e "${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} Example usage:"
    echo -e "${GREEN}║${NC}   lz-scan-quick 192.168.1.1"
    echo -e "${GREEN}║${NC}   lz-sql-test http://example.com/page.php?id=1"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
}

# Handle script arguments
case "${1:-}" in
    "--help"|"-h")
        echo "LeZelote-Toolkit Tools Configuration Script"
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --help, -h              Show this help message"
        echo "  --verify-only           Only verify existing configurations"
        echo "  --verbose               Enable verbose logging"
        exit 0
        ;;
    "--verify-only")
        if verify_tool_configurations; then
            log "SUCCESS" "All configurations are valid"
            exit 0
        else
            log "ERROR" "Some configurations are invalid"
            exit 1
        fi
        ;;
    "--verbose")
        set -x
        ;;
esac

# Run main configuration
main "$@"