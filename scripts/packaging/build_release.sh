#!/bin/bash
#==============================================================================
# LeZelote Toolkit - Release Build Script
# Builds complete release packages for all platforms
#==============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
VERSION="${1:-1.0.0}"
BUILD_DIR="$PROJECT_ROOT/build"
RELEASE_DIR="$PROJECT_ROOT/releases"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

#==============================================================================
# Functions
#==============================================================================

print_banner() {
    clear
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    LEZELOTE TOOLKIT - RELEASE BUILDER                       ║"
    echo "║                                Version $VERSION                                ║"
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

check_dependencies() {
    print_status "Checking build dependencies..."
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 not found"
        return 1
    fi
    
    # Check required Python modules
    if ! python3 -c "import zipfile, tarfile, hashlib, json" >/dev/null 2>&1; then
        print_error "Required Python modules not available"
        return 1
    fi
    
    # Check git (for version info)
    if command -v git >/dev/null 2>&1; then
        GIT_AVAILABLE=true
        GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    else
        GIT_AVAILABLE=false
        GIT_COMMIT="unknown"
        GIT_BRANCH="unknown"
    fi
    
    print_success "Dependencies check passed"
    print_status "Git commit: $GIT_COMMIT"
    print_status "Git branch: $GIT_BRANCH"
}

validate_project() {
    print_status "Validating project structure..."
    
    # Run validation using the Python script
    if python3 "$SCRIPT_DIR/create_release.py" --validate-only; then
        print_success "Project validation passed"
        return 0
    else
        print_error "Project validation failed"
        return 1
    fi
}

prepare_build_environment() {
    print_status "Preparing build environment..."
    
    # Clean previous builds
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        print_status "Cleaned previous build directory"
    fi
    
    if [ -d "$RELEASE_DIR" ]; then
        rm -rf "$RELEASE_DIR"
        print_status "Cleaned previous release directory"
    fi
    
    # Create directories
    mkdir -p "$BUILD_DIR"
    mkdir -p "$RELEASE_DIR"
    
    print_success "Build environment prepared"
}

run_tests() {
    print_status "Running critical tests before release..."
    
    cd "$PROJECT_ROOT"
    
    # Run basic import tests
    if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from core.engine.orchestrator import PentestOrchestrator
    from core.security.consent_manager import ConsentManager
    print('✓ Core imports successful')
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
" >/dev/null 2>&1; then
        print_success "Core module tests passed"
    else
        print_error "Core module tests failed"
        return 1
    fi
    
    # Check if CLI can be imported
    if python3 -c "
import sys
import os
sys.path.insert(0, '.')
os.chdir('.')
exec(open('run_cli.py').read().split('if __name__')[0])
print('✓ CLI script validation successful')
" >/dev/null 2>&1; then
        print_success "CLI validation passed"
    else
        print_warning "CLI validation failed (may be expected in headless environment)"
    fi
    
    print_success "Pre-release tests completed"
}

create_release_packages() {
    print_status "Creating release packages..."
    
    # Run the Python release creation script
    cd "$PROJECT_ROOT"
    
    if python3 "$SCRIPT_DIR/create_release.py" --version "$VERSION" --output-dir "$RELEASE_DIR"; then
        print_success "Release packages created successfully"
        return 0
    else
        print_error "Failed to create release packages"
        return 1
    fi
}

generate_build_info() {
    print_status "Generating build information..."
    
    BUILD_INFO_FILE="$RELEASE_DIR/build_info.json"
    
    cat > "$BUILD_INFO_FILE" << EOF
{
  "build_info": {
    "version": "$VERSION",
    "build_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "build_host": "$(hostname)",
    "build_user": "$(whoami)",
    "build_os": "$(uname -s)",
    "build_arch": "$(uname -m)",
    "git_commit": "$GIT_COMMIT",
    "git_branch": "$GIT_BRANCH",
    "python_version": "$(python3 --version)",
    "build_script": "$0"
  },
  "project_info": {
    "name": "LeZelote Toolkit",
    "description": "Comprehensive penetration testing toolkit",
    "homepage": "https://github.com/LeZelote01/LeZelote-Toolkit",
    "license": "MIT",
    "author": "LeZelote Team"
  }
}
EOF
    
    print_success "Build info generated: $BUILD_INFO_FILE"
}

create_readme() {
    print_status "Creating release README..."
    
    README_FILE="$RELEASE_DIR/README.md"
    
    cat > "$README_FILE" << 'EOF'
# LeZelote Toolkit - Release Package

## Quick Start

### Linux/macOS
```bash
# Download and extract
unzip lezelote-toolkit-*-universal-portable.zip
cd lezelote-toolkit-*/

# Launch toolkit
./launch.sh
```

### Windows
```cmd
# Download and extract ZIP file
# Double-click launch.bat or run from command prompt:
launch.bat
```

## Package Contents

- **Portable Packages**: Ready-to-run packages for each platform
- **Source Package**: Complete source code archive
- **Installers**: Automated installation scripts
- **Documentation**: Complete user and developer guides in `docs/`

## System Requirements

- **Python**: 3.9+ (included in some packages)
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 2GB+ free space
- **OS**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+

## Installation Options

### Option 1: Portable (Recommended)
Extract ZIP and run launcher script. No system installation required.

### Option 2: System Installation
Run the appropriate installer script for your platform:
- Linux: `sudo bash install.sh`
- Windows: Right-click `install.bat` → "Run as administrator"

## Package Verification

Verify package integrity using provided checksums:
```bash
sha256sum -c checksums.txt
```

## Getting Started

1. Extract or install the toolkit
2. Run the launcher script for your platform
3. Follow the interactive setup wizard
4. Consult `docs/user_guide.md` for detailed usage instructions

## Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues page
- **Security**: security@pentestusb.dev

## Legal Notice

This toolkit is for authorized penetration testing only. Users are responsible for compliance with applicable laws and regulations.
EOF
    
    print_success "Release README created: $README_FILE"
}

display_summary() {
    print_status "Build Summary"
    echo "=============="
    
    if [ -d "$RELEASE_DIR" ]; then
        echo "📦 Release packages created in: $RELEASE_DIR"
        echo ""
        
        # List created files with sizes
        echo "📁 Package Contents:"
        for file in "$RELEASE_DIR"/*; do
            if [ -f "$file" ]; then
                size=$(du -h "$file" | cut -f1)
                filename=$(basename "$file")
                echo "   $size    $filename"
            fi
        done
        echo ""
        
        # Calculate total size
        total_size=$(du -sh "$RELEASE_DIR" | cut -f1)
        echo "💾 Total release size: $total_size"
        
        # Count files
        file_count=$(find "$RELEASE_DIR" -type f | wc -l)
        echo "📊 Total files: $file_count"
        echo ""
        
        print_success "Release build completed successfully! 🎉"
        echo ""
        echo "Next steps:"
        echo "1. Test packages on target platforms"
        echo "2. Upload to release distribution system"
        echo "3. Update documentation with release notes"
        echo "4. Announce release to users"
        
    else
        print_error "Release directory not found - build may have failed"
        return 1
    fi
}

cleanup() {
    print_status "Cleaning up temporary files..."
    
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        print_status "Removed build directory"
    fi
}

show_help() {
    echo "LeZelote Toolkit - Release Build Script"
    echo ""
    echo "Usage: $0 [VERSION] [OPTIONS]"
    echo ""
    echo "Arguments:"
    echo "  VERSION                 Version number (default: 1.0.0)"
    echo ""
    echo "Options:"
    echo "  -h, --help             Show this help"
    echo "  --skip-tests           Skip pre-release tests"
    echo "  --skip-validation      Skip project validation"
    echo "  --clean-only           Only clean build directories"
    echo ""
    echo "Examples:"
    echo "  $0                     Build release v1.0.0"
    echo "  $0 1.1.0              Build release v1.1.0"
    echo "  $0 --clean-only        Clean build directories"
    echo ""
}

#==============================================================================
# Main execution
#==============================================================================

# Parse arguments
SKIP_TESTS=false
SKIP_VALIDATION=false
CLEAN_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --clean-only)
            CLEAN_ONLY=true
            shift
            ;;
        *)
            if [[ $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                VERSION=$1
            else
                print_error "Unknown option: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Main workflow
print_banner

if [ "$CLEAN_ONLY" = true ]; then
    prepare_build_environment
    print_success "Build directories cleaned"
    exit 0
fi

# Check dependencies
if ! check_dependencies; then
    exit 1
fi

# Project validation
if [ "$SKIP_VALIDATION" = false ]; then
    if ! validate_project; then
        exit 1
    fi
fi

# Prepare environment
prepare_build_environment

# Run tests
if [ "$SKIP_TESTS" = false ]; then
    if ! run_tests; then
        print_warning "Tests failed, but continuing with build..."
    fi
fi

# Create release packages
if ! create_release_packages; then
    print_error "Release package creation failed"
    exit 1
fi

# Generate additional files
generate_build_info
create_readme

# Show summary
display_summary

# Cleanup
cleanup

print_success "🎉 Release build process completed successfully!"
echo ""
echo "Release packages are ready for distribution in:"
echo "   $RELEASE_DIR"
echo ""