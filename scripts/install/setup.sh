#!/bin/bash
# =============================================================================
# LeZelote-Toolkit - Setup Script for Linux/macOS
# =============================================================================
# Description: Comprehensive installation script for UNIX-based systems
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly LOG_FILE="$PROJECT_ROOT/logs/installation.log"
readonly CONFIG_DIR="$PROJECT_ROOT/config"

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
║                       LeZelote-Toolkit Setup Script                          ║
║                           Linux/macOS Installation                           ║
║                                Version 1.0.0                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log "WARN" "Running as root. This is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "INFO" "Installation aborted by user"
            exit 1
        fi
    fi
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

check_system_requirements() {
    log "INFO" "Checking system requirements..."
    
    local os=$(detect_os)
    local cpu_cores=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "1")
    local total_memory
    
    if [[ "$os" == "macos" ]]; then
        total_memory=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    else
        total_memory=$(free -g | awk '/^Mem:/{print $2}')
    fi
    
    local disk_space=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print int($4)}')
    
    log "INFO" "System Information:"
    log "INFO" "  - OS: $os"
    log "INFO" "  - CPU Cores: $cpu_cores"
    log "INFO" "  - Memory: ${total_memory}GB"
    log "INFO" "  - Available Disk: ${disk_space}GB"
    
    # Requirements check
    local errors=0
    
    if [[ $cpu_cores -lt 2 ]]; then
        log "WARN" "Minimum 2 CPU cores recommended (found: $cpu_cores)"
    fi
    
    if [[ $total_memory -lt 8 ]]; then
        log "ERROR" "Minimum 8GB RAM required (found: ${total_memory}GB)"
        ((errors++))
    fi
    
    if [[ $disk_space -lt 32 ]]; then
        log "ERROR" "Minimum 32GB free disk space required (found: ${disk_space}GB)"
        ((errors++))
    fi
    
    if [[ $errors -gt 0 ]]; then
        log "ERROR" "System requirements not met. Please upgrade your system."
        exit 1
    fi
    
    log "SUCCESS" "System requirements check passed"
}

install_system_dependencies() {
    log "INFO" "Installing system dependencies..."
    
    local os=$(detect_os)
    
    case "$os" in
        "ubuntu")
            sudo apt-get update
            sudo apt-get install -y \
                python3 python3-pip python3-venv python3-dev \
                git curl wget unzip \
                build-essential cmake \
                libssl-dev libffi-dev \
                nmap masscan rustscan \
                docker.io docker-compose \
                tshark wireshark-common \
                aircrack-ng \
                john hashcat \
                sqlmap nikto \
                dirb gobuster \
                hydra medusa \
                metasploit-framework
            ;;
        "centos")
            sudo yum update -y
            sudo yum install -y epel-release
            sudo yum install -y \
                python3 python3-pip python3-devel \
                git curl wget unzip \
                gcc gcc-c++ make cmake \
                openssl-devel libffi-devel \
                nmap \
                docker docker-compose
            ;;
        "arch")
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm \
                python python-pip \
                git curl wget unzip \
                base-devel cmake \
                openssl libffi \
                nmap masscan \
                docker docker-compose \
                wireshark-cli \
                aircrack-ng \
                john hashcat \
                sqlmap
            ;;
        "macos")
            if ! command -v brew >/dev/null 2>&1; then
                log "INFO" "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew update
            brew install \
                python3 \
                git curl wget \
                cmake \
                nmap masscan \
                docker docker-compose \
                wireshark \
                aircrack-ng \
                john-jumbo hashcat \
                sqlmap
            ;;
        *)
            log "ERROR" "Unsupported operating system: $os"
            exit 1
            ;;
    esac
    
    log "SUCCESS" "System dependencies installed successfully"
}

setup_python_environment() {
    log "INFO" "Setting up Python environment..."
    
    # Create virtual environment
    if [[ ! -d "$PROJECT_ROOT/.venv" ]]; then
        python3 -m venv "$PROJECT_ROOT/.venv"
        log "INFO" "Python virtual environment created"
    fi
    
    # Activate virtual environment
    source "$PROJECT_ROOT/.venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        pip install -r "$PROJECT_ROOT/requirements.txt"
        log "SUCCESS" "Python dependencies installed successfully"
    else
        log "ERROR" "requirements.txt not found"
        exit 1
    fi
}

setup_docker_environment() {
    log "INFO" "Setting up Docker environment..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log "INFO" "Starting Docker service..."
        
        local os=$(detect_os)
        case "$os" in
            "ubuntu"|"centos"|"arch")
                sudo systemctl start docker
                sudo systemctl enable docker
                ;;
            "macos")
                open -a Docker
                log "INFO" "Please start Docker Desktop manually"
                ;;
        esac
        
        # Wait for Docker to start
        local retry=0
        while ! docker info >/dev/null 2>&1 && [[ $retry -lt 30 ]]; do
            log "INFO" "Waiting for Docker to start..."
            sleep 2
            ((retry++))
        done
        
        if ! docker info >/dev/null 2>&1; then
            log "ERROR" "Docker failed to start. Please start Docker manually and re-run setup."
            exit 1
        fi
    fi
    
    # Add user to docker group (Linux only)
    if [[ "$OSTYPE" == "linux-gnu"* ]] && ! groups | grep -q docker; then
        sudo usermod -aG docker "$USER"
        log "WARN" "Added user to docker group. Please logout and login again for changes to take effect."
    fi
    
    # Test Docker
    if docker run --rm hello-world >/dev/null 2>&1; then
        log "SUCCESS" "Docker setup completed successfully"
    else
        log "ERROR" "Docker test failed. Please check Docker installation."
        exit 1
    fi
}

create_directories() {
    log "INFO" "Creating directory structure..."
    
    local directories=(
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/outputs/scans"
        "$PROJECT_ROOT/outputs/reports"
        "$PROJECT_ROOT/outputs/temporary"
        "$PROJECT_ROOT/data/loot"
        "$PROJECT_ROOT/tools/binaries"
        "$HOME/.lezelote"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log "INFO" "Created directory: $dir"
        fi
    done
    
    log "SUCCESS" "Directory structure created successfully"
}

configure_permissions() {
    log "INFO" "Configuring file permissions..."
    
    # Make scripts executable
    find "$PROJECT_ROOT/scripts" -name "*.sh" -exec chmod +x {} \;
    find "$PROJECT_ROOT/scripts" -name "*.py" -exec chmod +x {} \;
    
    # Make launch scripts executable
    chmod +x "$PROJECT_ROOT/launch.sh" 2>/dev/null || true
    chmod +x "$PROJECT_ROOT/run_cli.py" 2>/dev/null || true
    
    # Set proper permissions for config directory
    chmod 750 "$CONFIG_DIR"
    find "$CONFIG_DIR" -name "*.yaml" -exec chmod 640 {} \;
    
    log "SUCCESS" "File permissions configured successfully"
}

setup_configuration() {
    log "INFO" "Setting up configuration files..."
    
    # Create user config if it doesn't exist
    local user_config="$HOME/.lezelote/config.yaml"
    if [[ ! -f "$user_config" ]]; then
        cat > "$user_config" << 'EOF'
# LeZelote-Toolkit User Configuration
user:
  name: ""
  email: ""
  organization: ""

paths:
  project_root: ""
  output_directory: ""
  tools_directory: ""

preferences:
  default_scan_profile: "default"
  auto_update: true
  stealth_mode: false
  verbose_logging: false

interface:
  theme: "dark"
  show_banner: true
  confirmation_prompts: true
EOF
        
        # Update project root path
        sed -i.bak "s|project_root: \"\"|project_root: \"$PROJECT_ROOT\"|" "$user_config"
        rm "$user_config.bak" 2>/dev/null || true
        
        log "INFO" "User configuration file created: $user_config"
    fi
    
    log "SUCCESS" "Configuration setup completed"
}

register_shell_aliases() {
    log "INFO" "Registering shell aliases..."
    
    local shell_rc=""
    if [[ -n "${BASH_VERSION:-}" ]]; then
        shell_rc="$HOME/.bashrc"
    elif [[ -n "${ZSH_VERSION:-}" ]]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.profile"
    fi
    
    local alias_line="alias lezelote='cd $PROJECT_ROOT && ./launch.sh'"
    
    if [[ -f "$shell_rc" ]] && ! grep -q "alias lezelote=" "$shell_rc"; then
        echo "" >> "$shell_rc"
        echo "# LeZelote-Toolkit aliases" >> "$shell_rc"
        echo "$alias_line" >> "$shell_rc"
        echo "export LEZELOTE_HOME=\"$PROJECT_ROOT\"" >> "$shell_rc"
        
        log "INFO" "Aliases added to $shell_rc"
        log "INFO" "Run 'source $shell_rc' or restart your terminal to use 'lezelote' command"
    fi
    
    log "SUCCESS" "Shell aliases registered successfully"
}

run_verification() {
    log "INFO" "Running installation verification..."
    
    if [[ -x "$SCRIPT_DIR/verify_installation.py" ]]; then
        python3 "$SCRIPT_DIR/verify_installation.py"
    else
        log "WARN" "Verification script not found. Skipping verification."
    fi
}

# =============================================================================
# Main Installation Process
# =============================================================================

main() {
    print_banner
    
    # Create logs directory first
    mkdir -p "$PROJECT_ROOT/logs"
    
    log "INFO" "Starting LeZelote-Toolkit installation..."
    log "INFO" "Installation directory: $PROJECT_ROOT"
    
    check_root
    check_system_requirements
    
    # Create directory structure
    create_directories
    
    # Install system dependencies
    if [[ "${SKIP_SYSTEM_DEPS:-false}" != "true" ]]; then
        install_system_dependencies
    else
        log "WARN" "Skipping system dependencies installation (SKIP_SYSTEM_DEPS=true)"
    fi
    
    # Setup Python environment
    setup_python_environment
    
    # Setup Docker
    if [[ "${SKIP_DOCKER:-false}" != "true" ]]; then
        setup_docker_environment
    else
        log "WARN" "Skipping Docker setup (SKIP_DOCKER=true)"
    fi
    
    # Configure permissions
    configure_permissions
    
    # Setup configuration
    setup_configuration
    
    # Register shell aliases
    register_shell_aliases
    
    # Run verification
    run_verification
    
    log "SUCCESS" "LeZelote-Toolkit installation completed successfully!"
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                          Installation Complete!                             ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC} To start using LeZelote-Toolkit:                                        ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                                          ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} 1. Restart your terminal or run: source ~/.bashrc                      ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} 2. Use command: lezelote                                               ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} 3. Or navigate to: $PROJECT_ROOT${NC}"
    echo -e "${GREEN}║${NC}    and run: ./launch.sh                                                ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                                          ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} Configuration file: ~/.lezelote/config.yaml                            ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} Log file: $LOG_FILE${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
}

# Handle script arguments
case "${1:-}" in
    "--help"|"-h")
        echo "LeZelote-Toolkit Setup Script"
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --help, -h              Show this help message"
        echo "  --skip-system-deps      Skip system dependencies installation"
        echo "  --skip-docker           Skip Docker setup"
        echo "  --verbose               Enable verbose logging"
        exit 0
        ;;
    "--skip-system-deps")
        export SKIP_SYSTEM_DEPS=true
        ;;
    "--skip-docker")
        export SKIP_DOCKER=true
        ;;
    "--verbose")
        set -x
        ;;
esac

# Run main installation
main "$@"