#!/bin/bash
# =============================================================================
# LeZelote-Toolkit - Update Download Script
# =============================================================================
# Description: Download updates and prepare them for installation
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly LOG_FILE="$PROJECT_ROOT/logs/download_updates.log"
readonly DOWNLOADS_DIR="$PROJECT_ROOT/downloads"
readonly TEMP_DIR="$PROJECT_ROOT/temp"

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
║                   LeZelote-Toolkit Update Download Manager                   ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "darwin" 
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

get_architecture() {
    local arch=$(uname -m)
    case "$arch" in
        x86_64|amd64)
            echo "amd64"
            ;;
        i386|i686)
            echo "386"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        armv7l)
            echo "armv7"
            ;;
        *)
            echo "$arch"
            ;;
    esac
}

check_dependencies() {
    log "INFO" "Checking required dependencies..."
    
    local missing_deps=()
    
    # Check for required commands
    local required_commands=("curl" "wget" "jq" "git")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log "ERROR" "Missing required dependencies: ${missing_deps[*]}"
        log "INFO" "Please install missing dependencies and try again"
        return 1
    fi
    
    log "SUCCESS" "All required dependencies are available"
    return 0
}

create_directories() {
    log "INFO" "Creating download directories..."
    
    local directories=(
        "$DOWNLOADS_DIR"
        "$DOWNLOADS_DIR/tools"
        "$DOWNLOADS_DIR/databases"
        "$DOWNLOADS_DIR/wordlists"
        "$DOWNLOADS_DIR/signatures"
        "$TEMP_DIR"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log "INFO" "Created directory: $dir"
        fi
    done
    
    log "SUCCESS" "Download directories created successfully"
}

download_with_progress() {
    local url="$1"
    local output_file="$2"
    local description="${3:-file}"
    
    log "INFO" "Downloading $description..."
    log "INFO" "URL: $url"
    log "INFO" "Output: $output_file"
    
    # Try curl first, fallback to wget
    if command -v curl >/dev/null 2>&1; then
        if curl -L --progress-bar --fail "$url" -o "$output_file"; then
            log "SUCCESS" "Downloaded $description successfully"
            return 0
        else
            log "ERROR" "Failed to download $description with curl"
            return 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget --progress=bar:force "$url" -O "$output_file"; then
            log "SUCCESS" "Downloaded $description successfully"
            return 0
        else
            log "ERROR" "Failed to download $description with wget"
            return 1
        fi
    else
        log "ERROR" "Neither curl nor wget is available"
        return 1
    fi
}

verify_checksum() {
    local file_path="$1"
    local expected_checksum="$2"
    local algorithm="${3:-sha256}"
    
    if [[ -z "$expected_checksum" ]]; then
        log "WARN" "No checksum provided for verification"
        return 0
    fi
    
    log "INFO" "Verifying checksum for $(basename "$file_path")..."
    
    local actual_checksum
    case "$algorithm" in
        "sha256")
            actual_checksum=$(sha256sum "$file_path" | cut -d' ' -f1)
            ;;
        "sha1")
            actual_checksum=$(sha1sum "$file_path" | cut -d' ' -f1)
            ;;
        "md5")
            actual_checksum=$(md5sum "$file_path" | cut -d' ' -f1)
            ;;
        *)
            log "ERROR" "Unsupported checksum algorithm: $algorithm"
            return 1
            ;;
    esac
    
    if [[ "$actual_checksum" == "$expected_checksum" ]]; then
        log "SUCCESS" "Checksum verification passed"
        return 0
    else
        log "ERROR" "Checksum verification failed"
        log "ERROR" "Expected: $expected_checksum"
        log "ERROR" "Actual: $actual_checksum"
        return 1
    fi
}

get_github_latest_release() {
    local repo="$1"
    local include_prereleases="${2:-false}"
    
    local api_url="https://api.github.com/repos/$repo/releases"
    
    if [[ "$include_prereleases" == "false" ]]; then
        api_url="$api_url/latest"
        
        local release_info
        if release_info=$(curl -s "$api_url"); then
            echo "$release_info"
            return 0
        else
            log "ERROR" "Failed to get latest release for $repo"
            return 1
        fi
    else
        local releases_info
        if releases_info=$(curl -s "$api_url"); then
            echo "$releases_info" | jq '.[0]'
            return 0
        else
            log "ERROR" "Failed to get releases for $repo"
            return 1
        fi
    fi
}

download_github_release_asset() {
    local repo="$1"
    local asset_pattern="$2"
    local output_dir="$3"
    local description="${4:-GitHub release asset}"
    
    log "INFO" "Downloading $description from $repo..."
    
    local release_info
    if ! release_info=$(get_github_latest_release "$repo"); then
        return 1
    fi
    
    local tag_name
    tag_name=$(echo "$release_info" | jq -r '.tag_name')
    
    local assets
    assets=$(echo "$release_info" | jq -r '.assets[]')
    
    local matching_asset
    matching_asset=$(echo "$assets" | jq -r "select(.name | test(\"$asset_pattern\")) | .browser_download_url" | head -1)
    
    if [[ -z "$matching_asset" ]] || [[ "$matching_asset" == "null" ]]; then
        log "ERROR" "No matching asset found for pattern: $asset_pattern"
        return 1
    fi
    
    local asset_name
    asset_name=$(basename "$matching_asset")
    local output_file="$output_dir/$asset_name"
    
    if download_with_progress "$matching_asset" "$output_file" "$description"; then
        echo "$output_file"
        return 0
    else
        return 1
    fi
}

download_git_repository() {
    local repo_url="$1"
    local local_dir="$2"
    local branch="${3:-main}"
    
    log "INFO" "Downloading Git repository: $repo_url"
    
    if [[ -d "$local_dir/.git" ]]; then
        log "INFO" "Repository already exists, updating..."
        cd "$local_dir"
        
        if git fetch origin "$branch" && git reset --hard "origin/$branch"; then
            log "SUCCESS" "Repository updated successfully"
            return 0
        else
            log "ERROR" "Failed to update repository"
            return 1
        fi
    else
        log "INFO" "Cloning repository..."
        
        if git clone --depth 1 --branch "$branch" "$repo_url" "$local_dir"; then
            log "SUCCESS" "Repository cloned successfully"
            return 0
        else
            log "ERROR" "Failed to clone repository"
            return 1
        fi
    fi
}

# =============================================================================
# Download Functions for Specific Components
# =============================================================================

download_nuclei() {
    log "INFO" "Downloading Nuclei..."
    
    local os=$(detect_os)
    local arch=$(get_architecture)
    
    local asset_pattern
    case "$os" in
        "linux")
            asset_pattern="nuclei_.*_linux_${arch}\\.zip"
            ;;
        "darwin")
            asset_pattern="nuclei_.*_darwin_${arch}\\.zip"
            ;;
        "windows")
            asset_pattern="nuclei_.*_windows_${arch}\\.zip"
            ;;
        *)
            log "ERROR" "Unsupported OS for Nuclei: $os"
            return 1
            ;;
    esac
    
    local downloaded_file
    if downloaded_file=$(download_github_release_asset "projectdiscovery/nuclei" "$asset_pattern" "$DOWNLOADS_DIR/tools" "Nuclei"); then
        log "SUCCESS" "Nuclei downloaded: $downloaded_file"
        return 0
    else
        return 1
    fi
}

download_subfinder() {
    log "INFO" "Downloading Subfinder..."
    
    local os=$(detect_os)
    local arch=$(get_architecture)
    
    local asset_pattern="subfinder_.*_${os}_${arch}\\.zip"
    
    local downloaded_file
    if downloaded_file=$(download_github_release_asset "projectdiscovery/subfinder" "$asset_pattern" "$DOWNLOADS_DIR/tools" "Subfinder"); then
        log "SUCCESS" "Subfinder downloaded: $downloaded_file"
        return 0
    else
        return 1
    fi
}

download_httpx() {
    log "INFO" "Downloading HTTPx..."
    
    local os=$(detect_os)
    local arch=$(get_architecture)
    
    local asset_pattern="httpx_.*_${os}_${arch}\\.zip"
    
    local downloaded_file
    if downloaded_file=$(download_github_release_asset "projectdiscovery/httpx" "$asset_pattern" "$DOWNLOADS_DIR/tools" "HTTPx"); then
        log "SUCCESS" "HTTPx downloaded: $downloaded_file"
        return 0
    else
        return 1
    fi
}

download_gobuster() {
    log "INFO" "Downloading Gobuster..."
    
    local os=$(detect_os)
    local arch=$(get_architecture)
    
    local asset_pattern
    case "$os" in
        "linux")
            asset_pattern="gobuster-${os}-${arch}\\.tar\\.gz"
            ;;
        "darwin")
            asset_pattern="gobuster-${os}-${arch}\\.tar\\.gz"
            ;;
        "windows")
            asset_pattern="gobuster-${os}-${arch}\\.zip"
            ;;
        *)
            log "ERROR" "Unsupported OS for Gobuster: $os"
            return 1
            ;;
    esac
    
    local downloaded_file
    if downloaded_file=$(download_github_release_asset "OJ/gobuster" "$asset_pattern" "$DOWNLOADS_DIR/tools" "Gobuster"); then
        log "SUCCESS" "Gobuster downloaded: $downloaded_file"
        return 0
    else
        return 1
    fi
}

download_ffuf() {
    log "INFO" "Downloading FFuF..."
    
    local os=$(detect_os)
    local arch=$(get_architecture)
    
    local asset_pattern="ffuf_.*_${os}_${arch}\\.tar\\.gz"
    
    local downloaded_file
    if downloaded_file=$(download_github_release_asset "ffuf/ffuf" "$asset_pattern" "$DOWNLOADS_DIR/tools" "FFuF"); then
        log "SUCCESS" "FFuF downloaded: $downloaded_file"
        return 0
    else
        return 1
    fi
}

download_nuclei_templates() {
    log "INFO" "Downloading Nuclei Templates..."
    
    local templates_dir="$DOWNLOADS_DIR/databases/nuclei-templates"
    
    if download_git_repository "https://github.com/projectdiscovery/nuclei-templates.git" "$templates_dir"; then
        log "SUCCESS" "Nuclei Templates downloaded"
        return 0
    else
        return 1
    fi
}

download_seclists() {
    log "INFO" "Downloading SecLists..."
    
    local seclists_dir="$DOWNLOADS_DIR/wordlists/SecLists"
    
    if download_git_repository "https://github.com/danielmiessler/SecLists.git" "$seclists_dir"; then
        log "SUCCESS" "SecLists downloaded"
        return 0
    else
        return 1
    fi
}

download_payloads_all_the_things() {
    log "INFO" "Downloading PayloadsAllTheThings..."
    
    local payloads_dir="$DOWNLOADS_DIR/databases/PayloadsAllTheThings"
    
    if download_git_repository "https://github.com/swisskyrepo/PayloadsAllTheThings.git" "$payloads_dir"; then
        log "SUCCESS" "PayloadsAllTheThings downloaded"
        return 0
    else
        return 1
    fi
}

download_cve_database() {
    log "INFO" "Downloading CVE Database..."
    
    local cve_url="https://cve.mitre.org/data/downloads/allitems.csv"
    local output_file="$DOWNLOADS_DIR/databases/cve_database.csv"
    
    if download_with_progress "$cve_url" "$output_file" "CVE Database"; then
        log "SUCCESS" "CVE Database downloaded"
        return 0
    else
        return 1
    fi
}

download_exploit_database() {
    log "INFO" "Downloading Exploit Database..."
    
    local edb_url="https://gitlab.com/exploit-database/exploitdb/-/raw/main/files_exploits.csv"
    local output_file="$DOWNLOADS_DIR/databases/exploit_database.csv"
    
    if download_with_progress "$edb_url" "$output_file" "Exploit Database"; then
        log "SUCCESS" "Exploit Database downloaded"
        return 0
    else
        return 1
    fi
}

# =============================================================================
# Main Download Functions
# =============================================================================

download_tools() {
    log "INFO" "Starting tools download..."
    
    local tools=(
        "nuclei"
        "subfinder" 
        "httpx"
        "gobuster"
        "ffuf"
    )
    
    local failed_downloads=()
    
    for tool in "${tools[@]}"; do
        if "download_$tool"; then
            log "SUCCESS" "$tool download completed"
        else
            log "ERROR" "$tool download failed"
            failed_downloads+=("$tool")
        fi
    done
    
    if [[ ${#failed_downloads[@]} -eq 0 ]]; then
        log "SUCCESS" "All tools downloaded successfully"
        return 0
    else
        log "ERROR" "Failed to download: ${failed_downloads[*]}"
        return 1
    fi
}

download_databases() {
    log "INFO" "Starting databases download..."
    
    local databases=(
        "nuclei_templates"
        "payloads_all_the_things"
        "cve_database"
        "exploit_database"
    )
    
    local failed_downloads=()
    
    for database in "${databases[@]}"; do
        if "download_$database"; then
            log "SUCCESS" "$database download completed"
        else
            log "ERROR" "$database download failed"
            failed_downloads+=("$database")
        fi
    done
    
    if [[ ${#failed_downloads[@]} -eq 0 ]]; then
        log "SUCCESS" "All databases downloaded successfully"
        return 0
    else
        log "ERROR" "Failed to download: ${failed_downloads[*]}"
        return 1
    fi
}

download_wordlists() {
    log "INFO" "Starting wordlists download..."
    
    local wordlists=(
        "seclists"
    )
    
    local failed_downloads=()
    
    for wordlist in "${wordlists[@]}"; do
        if "download_$wordlist"; then
            log "SUCCESS" "$wordlist download completed"
        else
            log "ERROR" "$wordlist download failed"
            failed_downloads+=("$wordlist")
        fi
    done
    
    if [[ ${#failed_downloads[@]} -eq 0 ]]; then
        log "SUCCESS" "All wordlists downloaded successfully"
        return 0
    else
        log "ERROR" "Failed to download: ${failed_downloads[*]}"
        return 1
    fi
}

download_all() {
    log "INFO" "Starting download of all components..."
    
    local failed_components=()
    
    if download_tools; then
        log "SUCCESS" "Tools download completed"
    else
        failed_components+=("tools")
    fi
    
    if download_databases; then
        log "SUCCESS" "Databases download completed"
    else
        failed_components+=("databases")
    fi
    
    if download_wordlists; then
        log "SUCCESS" "Wordlists download completed"
    else
        failed_components+=("wordlists")
    fi
    
    if [[ ${#failed_components[@]} -eq 0 ]]; then
        log "SUCCESS" "All components downloaded successfully"
        return 0
    else
        log "ERROR" "Failed components: ${failed_components[*]}"
        return 1
    fi
}

cleanup_downloads() {
    log "INFO" "Cleaning up temporary files..."
    
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"/*
        log "SUCCESS" "Temporary files cleaned up"
    fi
}

show_download_summary() {
    log "INFO" "Download Summary:"
    
    if [[ -d "$DOWNLOADS_DIR" ]]; then
        local total_size=$(du -sh "$DOWNLOADS_DIR" 2>/dev/null | cut -f1)
        log "INFO" "Total downloads size: $total_size"
        
        log "INFO" "Downloaded files:"
        find "$DOWNLOADS_DIR" -type f -exec ls -lh {} \; | while read -r line; do
            local size=$(echo "$line" | awk '{print $5}')
            local file=$(echo "$line" | awk '{print $9}')
            log "INFO" "  - $(basename "$file"): $size"
        done
    fi
}

# =============================================================================
# Main Script Logic
# =============================================================================

main() {
    print_banner
    
    log "INFO" "Starting LeZelote-Toolkit update download..."
    log "INFO" "OS: $(detect_os)"
    log "INFO" "Architecture: $(get_architecture)"
    
    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi
    
    # Create directories
    create_directories
    
    # Parse arguments
    local component="${1:-all}"
    
    case "$component" in
        "tools")
            download_tools
            ;;
        "databases")
            download_databases
            ;;
        "wordlists")
            download_wordlists
            ;;
        "all")
            download_all
            ;;
        "cleanup")
            cleanup_downloads
            ;;
        *)
            echo "Usage: $0 {tools|databases|wordlists|all|cleanup}"
            echo "Available components:"
            echo "  tools      - Download security tools"
            echo "  databases  - Download vulnerability databases"
            echo "  wordlists  - Download wordlists"
            echo "  all        - Download all components"
            echo "  cleanup    - Clean up temporary files"
            exit 1
            ;;
    esac
    
    local exit_code=$?
    
    # Show summary if downloads were performed
    if [[ "$component" != "cleanup" ]]; then
        show_download_summary
    fi
    
    # Cleanup on success
    if [[ $exit_code -eq 0 ]] && [[ "$component" != "cleanup" ]]; then
        cleanup_downloads
    fi
    
    if [[ $exit_code -eq 0 ]]; then
        log "SUCCESS" "Update download completed successfully!"
    else
        log "ERROR" "Update download failed!"
    fi
    
    exit $exit_code
}

# Handle script arguments
case "${1:-}" in
    "--help"|"-h")
        echo "LeZelote-Toolkit Update Download Script"
        echo "Usage: $0 [component] [options]"
        echo ""
        echo "Components:"
        echo "  tools      Download security tools"
        echo "  databases  Download vulnerability databases"
        echo "  wordlists  Download wordlists"
        echo "  all        Download all components (default)"
        echo "  cleanup    Clean up temporary files"
        echo ""
        echo "Options:"
        echo "  --help, -h         Show this help message"
        echo "  --verbose          Enable verbose logging"
        echo ""
        echo "Examples:"
        echo "  $0 tools          # Download only tools"
        echo "  $0 databases      # Download only databases"
        echo "  $0 all            # Download everything"
        exit 0
        ;;
    "--verbose")
        set -x
        shift
        ;;
esac

# Run main function
main "$@"