#!/bin/bash
#==============================================================================
# LeZelote Toolkit - Launcher Script for Linux/macOS
# Version: 1.0.0
# Compatible: Linux, macOS, Windows (via WSL)
#==============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Toolkit information
TOOLKIT_NAME="LeZelote Toolkit"
VERSION="1.0.0"
AUTHOR="LeZelote Team"

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD=""
VENV_PATH="$SCRIPT_DIR/venv"

#==============================================================================
# Functions
#==============================================================================

print_banner() {
    clear
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                              ║"
    echo "║    ██╗     ███████╗███████╗███████╗██╗      ██████╗ ████████╗███████╗       ║"
    echo "║    ██║     ██╔════╝╚══███╔╝██╔════╝██║     ██╔═══██╗╚══██╔══╝██╔════╝       ║"
    echo "║    ██║     █████╗    ███╔╝ █████╗  ██║     ██║   ██║   ██║   █████╗         ║"
    echo "║    ██║     ██╔══╝   ███╔╝  ██╔══╝  ██║     ██║   ██║   ██║   ██╔══╝         ║"
    echo "║    ███████╗███████╗███████╗███████╗███████╗╚██████╔╝   ██║   ███████╗       ║"
    echo "║    ╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚══════╝       ║"
    echo "║                                                                              ║"
    echo "║                            PENTEST USB TOOLKIT                              ║"
    echo "║                                Version $VERSION                                ║"
    echo "║                                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_system() {
    print_status "Checking system compatibility..."
    
    # Detect OS
    case "$(uname -s)" in
        Linux*)     OS="Linux";;
        Darwin*)    OS="macOS";;
        CYGWIN*)    OS="Windows";;
        MINGW*)     OS="Windows";;
        MSYS*)      OS="Windows";;
        *)          OS="Unknown";;
    esac
    
    print_status "Detected OS: $OS"
    
    # Check architecture
    ARCH=$(uname -m)
    print_status "Architecture: $ARCH"
    
    # Check available memory
    if command -v free >/dev/null 2>&1; then
        MEMORY_MB=$(free -m | awk 'NR==2{print $2}')
        print_status "Available RAM: ${MEMORY_MB}MB"
        
        if [ "$MEMORY_MB" -lt 4096 ]; then
            print_warning "Low memory detected. Minimum 4GB recommended for optimal performance."
        fi
    fi
    
    # Check disk space
    DISK_SPACE=$(df -h "$SCRIPT_DIR" | awk 'NR==2 {print $4}')
    print_status "Available disk space: $DISK_SPACE"
}

find_python() {
    print_status "Looking for Python installation..."
    
    # Try different Python commands
    for cmd in python3.11 python3.10 python3.9 python3 python; do
        if command -v $cmd >/dev/null 2>&1; then
            VERSION_OUTPUT=$($cmd --version 2>&1)
            if [[ $VERSION_OUTPUT == *"Python 3."* ]]; then
                PYTHON_VERSION=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
                if [ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) -eq 1 ] 2>/dev/null || python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
                    PYTHON_CMD=$cmd
                    print_success "Found Python: $cmd ($VERSION_OUTPUT)"
                    return 0
                fi
            fi
        fi
    done
    
    print_error "Python 3.9+ not found. Please install Python 3.9 or higher."
    return 1
}

check_dependencies() {
    print_status "Checking Python dependencies..."
    
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found!"
        return 1
    fi
    
    # Check if virtual environment exists
    if [ -d "$VENV_PATH" ]; then
        print_status "Virtual environment found"
        source "$VENV_PATH/bin/activate"
        
        # Check if dependencies are installed
        if $PYTHON_CMD -c "import requests, nmap, yaml" >/dev/null 2>&1; then
            print_success "Dependencies are installed"
            return 0
        else
            print_warning "Some dependencies missing, installing..."
        fi
    else
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
    fi
    
    # Install/upgrade dependencies
    pip install --upgrade pip >/dev/null 2>&1
    if pip install -r "$SCRIPT_DIR/requirements.txt" >/dev/null 2>&1; then
        print_success "Dependencies installed successfully"
        return 0
    else
        print_error "Failed to install dependencies"
        return 1
    fi
}

check_tools() {
    print_status "Checking external tools availability..."
    
    # List of optional tools
    TOOLS=("nmap" "sqlmap" "dirb" "nikto" "hydra" "john" "hashcat")
    MISSING_TOOLS=()
    
    for tool in "${TOOLS[@]}"; do
        if command -v $tool >/dev/null 2>&1; then
            print_success "$tool: Available"
        else
            print_warning "$tool: Not found in PATH"
            MISSING_TOOLS+=($tool)
        fi
    done
    
    # Check for integrated binaries
    if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
        print_status "Checking integrated binaries..."
        
        BINARY_DIR="$SCRIPT_DIR/tools/binaries"
        case $OS in
            "Linux")
                BINARY_PATH="$BINARY_DIR/linux"
                ;;
            "macOS")
                BINARY_PATH="$BINARY_DIR/macos"
                ;;
            *)
                print_warning "No integrated binaries for $OS"
                BINARY_PATH=""
                ;;
        esac
        
        if [ -n "$BINARY_PATH" ] && [ -d "$BINARY_PATH" ]; then
            FOUND_BINARIES=$(find "$BINARY_PATH" -type f -executable | wc -l)
            print_status "Found $FOUND_BINARIES integrated binaries"
        fi
    fi
}

run_system_check() {
    print_status "Running comprehensive system check..."
    
    if [ -f "$SCRIPT_DIR/scripts/maintenance/system_check.py" ]; then
        $PYTHON_CMD "$SCRIPT_DIR/scripts/maintenance/system_check.py" --component resources
    else
        print_warning "System check script not found, skipping detailed analysis"
    fi
}

launch_toolkit() {
    print_status "Launching LeZelote Toolkit..."
    
    # Ensure we're in the toolkit directory
    cd "$SCRIPT_DIR"
    
    # Activate virtual environment if it exists
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
    fi
    
    # Check if CLI script exists
    if [ -f "$SCRIPT_DIR/run_cli.py" ]; then
        print_success "Starting CLI interface..."
        echo ""
        exec $PYTHON_CMD "$SCRIPT_DIR/run_cli.py"
    else
        print_error "CLI script (run_cli.py) not found!"
        exit 1
    fi
}

show_help() {
    echo -e "${WHITE}LeZelote Toolkit Launcher${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -v, --version           Show version information"
    echo "  -c, --check-only        Run system checks only (don't launch)"
    echo "  -s, --skip-checks       Skip system checks and launch directly"
    echo "  -w, --web               Launch web interface instead of CLI"
    echo "  --install-deps          Install/update dependencies only"
    echo "  --reset-venv            Reset virtual environment"
    echo ""
    echo "Examples:"
    echo "  $0                      Launch toolkit with system checks"
    echo "  $0 -s                   Launch toolkit without checks"
    echo "  $0 -w                   Launch web interface"
    echo "  $0 --install-deps       Install dependencies only"
    echo ""
}

show_version() {
    echo -e "${WHITE}$TOOLKIT_NAME${NC}"
    echo "Version: $VERSION"
    echo "Author: $AUTHOR"
    echo "Platform: $OS ($ARCH)"
    echo ""
}

launch_web_interface() {
    print_status "Launching web interface..."
    
    cd "$SCRIPT_DIR"
    
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
    fi
    
    if [ -f "$SCRIPT_DIR/interfaces/web/app.py" ]; then
        print_success "Starting web interface on http://localhost:8080"
        exec $PYTHON_CMD "$SCRIPT_DIR/interfaces/web/app.py"
    else
        print_error "Web interface not found!"
        exit 1
    fi
}

install_dependencies_only() {
    print_status "Installing dependencies only..."
    
    if find_python && check_dependencies; then
        print_success "Dependencies installation completed"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

reset_venv() {
    print_status "Resetting virtual environment..."
    
    if [ -d "$VENV_PATH" ]; then
        rm -rf "$VENV_PATH"
        print_success "Virtual environment removed"
    fi
    
    if find_python && check_dependencies; then
        print_success "Virtual environment recreated"
    else
        print_error "Failed to recreate virtual environment"
        exit 1
    fi
}

#==============================================================================
# Main execution
#==============================================================================

# Parse command line arguments
SKIP_CHECKS=false
CHECK_ONLY=false
WEB_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        -c|--check-only)
            CHECK_ONLY=true
            shift
            ;;
        -s|--skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        -w|--web)
            WEB_MODE=true
            shift
            ;;
        --install-deps)
            print_banner
            install_dependencies_only
            exit 0
            ;;
        --reset-venv)
            print_banner
            reset_venv
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Main workflow
print_banner

if [ "$SKIP_CHECKS" = false ]; then
    check_system
    
    if ! find_python; then
        exit 1
    fi
    
    if ! check_dependencies; then
        exit 1
    fi
    
    check_tools
    run_system_check
    
    print_success "System checks completed successfully!"
    echo ""
fi

if [ "$CHECK_ONLY" = true ]; then
    print_success "System check completed. Exiting."
    exit 0
fi

# Launch appropriate interface
if [ "$WEB_MODE" = true ]; then
    launch_web_interface
else
    launch_toolkit
fi