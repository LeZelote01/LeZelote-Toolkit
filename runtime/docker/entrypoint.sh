#!/bin/bash

# =============================================================================
# PENTEST-USB TOOLKIT - DOCKER ENTRYPOINT SCRIPT
# =============================================================================
# Container initialization and service startup script
# Handles environment setup, health checks, and graceful shutdown
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURATION & GLOBALS
# =============================================================================

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PENTEST_HOME="${PENTEST_HOME:-/opt/pentest-usb}"
PENTEST_DATA="${PENTEST_DATA:-/opt/pentest-usb/data}"
PENTEST_LOGS="${PENTEST_LOGS:-/var/log/pentest}"
PENTEST_OUTPUT="${PENTEST_OUTPUT:-/opt/pentest-usb/outputs}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
PYTHONPATH="${PENTEST_HOME}:${PYTHONPATH:-}"

# Service configuration
SERVICE_NAME="${SERVICE_NAME:-pentest-orchestrator}"
SERVICE_PORT="${SERVICE_PORT:-8080}"
HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-http://localhost:${SERVICE_PORT}/health}"

# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        ERROR)   echo -e "${RED}[${timestamp}] [${SERVICE_NAME}] [ERROR] ${message}${NC}" ;;
        WARN)    echo -e "${YELLOW}[${timestamp}] [${SERVICE_NAME}] [WARN] ${message}${NC}" ;;
        INFO)    echo -e "${GREEN}[${timestamp}] [${SERVICE_NAME}] [INFO] ${message}${NC}" ;;
        DEBUG)   [[ "$LOG_LEVEL" == "DEBUG" ]] && echo -e "${BLUE}[${timestamp}] [${SERVICE_NAME}] [DEBUG] ${message}${NC}" ;;
        SUCCESS) echo -e "${CYAN}[${timestamp}] [${SERVICE_NAME}] [SUCCESS] ${message}${NC}" ;;
        *)       echo -e "[${timestamp}] [${SERVICE_NAME}] ${message}" ;;
    esac
}

# =============================================================================
# INITIALIZATION FUNCTIONS
# =============================================================================

show_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    PENTEST-USB CONTAINER                    ║
║                      Starting Service...                    ║
╚══════════════════════════════════════════════════════════════╝
EOF
}

check_environment() {
    log "INFO" "Checking container environment..."
    
    # Verify required directories exist
    local required_dirs=(
        "$PENTEST_HOME"
        "$PENTEST_DATA"
        "$PENTEST_LOGS"
        "$PENTEST_OUTPUT"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log "WARN" "Creating missing directory: $dir"
            mkdir -p "$dir"
        fi
        
        # Ensure proper permissions
        if [[ -w "$dir" ]]; then
            log "DEBUG" "Directory writable: $dir"
        else
            log "WARN" "Directory not writable: $dir"
        fi
    done
    
    # Check Python environment
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python3 not found in container"
        exit 1
    fi
    
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log "INFO" "Python version: $python_version"
    
    # Verify PYTHONPATH
    export PYTHONPATH="$PENTEST_HOME:$PYTHONPATH"
    log "DEBUG" "PYTHONPATH: $PYTHONPATH"
    
    log "SUCCESS" "Environment check completed"
}

setup_database() {
    log "INFO" "Setting up database connections..."
    
    # Wait for PostgreSQL if it's a dependency
    if [[ -n "${POSTGRES_CONNECTION:-}" ]]; then
        local postgres_host=$(echo "$POSTGRES_CONNECTION" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        local postgres_port=$(echo "$POSTGRES_CONNECTION" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [[ -n "$postgres_host" && -n "$postgres_port" ]]; then
            log "INFO" "Waiting for PostgreSQL at $postgres_host:$postgres_port..."
            
            local attempts=0
            local max_attempts=30
            
            while [[ $attempts -lt $max_attempts ]]; do
                if nc -z "$postgres_host" "$postgres_port" 2>/dev/null; then
                    log "SUCCESS" "PostgreSQL is available"
                    break
                fi
                
                attempts=$((attempts + 1))
                log "DEBUG" "PostgreSQL not ready, attempt $attempts/$max_attempts"
                sleep 2
            done
            
            if [[ $attempts -eq $max_attempts ]]; then
                log "ERROR" "PostgreSQL not available after ${max_attempts} attempts"
                exit 1
            fi
        fi
    fi
    
    # Initialize SQLite databases if needed
    local sqlite_dbs=(
        "${PENTEST_DATA}/databases/project_db.sqlite"
        "${PENTEST_DATA}/databases/vuln_db.sqlite"
        "${PENTEST_HOME}/core/db/knowledge_base.db"
    )
    
    for db in "${sqlite_dbs[@]}"; do
        if [[ ! -f "$db" ]]; then
            log "INFO" "Creating SQLite database: $db"
            mkdir -p "$(dirname "$db")"
            touch "$db"
        fi
    done
    
    log "SUCCESS" "Database setup completed"
}

setup_logging() {
    log "INFO" "Configuring logging..."
    
    # Create log directories
    local log_dirs=(
        "${PENTEST_LOGS}/system"
        "${PENTEST_LOGS}/tools"
        "${PENTEST_LOGS}/scans"
        "${PENTEST_LOGS}/api"
    )
    
    for log_dir in "${log_dirs[@]}"; do
        mkdir -p "$log_dir"
    done
    
    # Configure Python logging
    export PENTEST_LOG_LEVEL="$LOG_LEVEL"
    export PENTEST_LOG_DIR="$PENTEST_LOGS"
    
    log "SUCCESS" "Logging configuration completed"
}

initialize_modules() {
    log "INFO" "Initializing Pentest-USB modules..."
    
    cd "$PENTEST_HOME"
    
    # Verify core modules are available
    local core_modules=(
        "core.engine.orchestrator"
        "core.security.stealth_engine"
        "core.utils.logging_handler"
        "modules.reconnaissance"
        "modules.vulnerability"
        "modules.exploitation"
        "modules.post_exploit"
        "modules.reporting"
    )
    
    for module in "${core_modules[@]}"; do
        if python3 -c "import ${module}" 2>/dev/null; then
            log "DEBUG" "Module available: $module"
        else
            log "WARN" "Module not available: $module"
        fi
    done
    
    # Initialize configuration
    if [[ -f "${PENTEST_HOME}/config/main_config.yaml" ]]; then
        export PENTEST_CONFIG="${PENTEST_HOME}/config/main_config.yaml"
        log "DEBUG" "Configuration loaded: $PENTEST_CONFIG"
    else
        log "WARN" "Main configuration not found"
    fi
    
    log "SUCCESS" "Module initialization completed"
}

setup_security() {
    log "INFO" "Applying security configurations..."
    
    # Set secure umask
    umask 0027
    
    # Clear sensitive environment variables if not needed
    unset POSTGRES_PASSWORD 2>/dev/null || true
    unset REDIS_PASSWORD 2>/dev/null || true
    unset NESSUS_ACTIVATION_CODE 2>/dev/null || true
    unset BURP_LICENSE_KEY 2>/dev/null || true
    
    # Ensure proper file permissions
    find "$PENTEST_HOME" -type f -name "*.py" -exec chmod 644 {} \; 2>/dev/null || true
    find "$PENTEST_HOME" -type f -name "*.sh" -exec chmod 755 {} \; 2>/dev/null || true
    
    log "SUCCESS" "Security configuration completed"
}

# =============================================================================
# HEALTH CHECK FUNCTIONS
# =============================================================================

health_check() {
    log "DEBUG" "Performing health check..."
    
    # Check if service port is listening
    if ! netstat -tln | grep -q ":${SERVICE_PORT} "; then
        log "ERROR" "Service port $SERVICE_PORT is not listening"
        return 1
    fi
    
    # HTTP health check if URL is available
    if [[ "$HEALTH_CHECK_URL" =~ ^http ]]; then
        if curl -sf "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            log "DEBUG" "HTTP health check passed"
        else
            log "WARN" "HTTP health check failed"
            return 1
        fi
    fi
    
    # Check disk space
    local disk_usage=$(df "$PENTEST_DATA" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        log "WARN" "Disk usage high: ${disk_usage}%"
    fi
    
    # Check memory usage
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [[ $mem_usage -gt 90 ]]; then
        log "WARN" "Memory usage high: ${mem_usage}%"
    fi
    
    log "DEBUG" "Health check completed"
    return 0
}

start_health_monitor() {
    log "INFO" "Starting health monitor..."
    
    (
        while true; do
            sleep 30
            if ! health_check; then
                log "ERROR" "Health check failed"
                # Could trigger alerts or graceful restart here
            fi
        done
    ) &
    
    echo $! > "/tmp/${SERVICE_NAME}_health_monitor.pid"
    log "INFO" "Health monitor started (PID: $(cat /tmp/${SERVICE_NAME}_health_monitor.pid))"
}

# =============================================================================
# SERVICE MANAGEMENT
# =============================================================================

start_service() {
    log "INFO" "Starting $SERVICE_NAME..."
    
    cd "$PENTEST_HOME"
    
    # Execute the main command
    log "INFO" "Executing: $*"
    exec "$@"
}

cleanup() {
    log "INFO" "Performing cleanup..."
    
    # Stop health monitor if running
    if [[ -f "/tmp/${SERVICE_NAME}_health_monitor.pid" ]]; then
        local monitor_pid=$(cat "/tmp/${SERVICE_NAME}_health_monitor.pid")
        if kill "$monitor_pid" 2>/dev/null; then
            log "INFO" "Health monitor stopped"
        fi
        rm -f "/tmp/${SERVICE_NAME}_health_monitor.pid"
    fi
    
    # Clean temporary files
    rm -rf /tmp/pentest_* 2>/dev/null || true
    
    log "INFO" "Cleanup completed"
}

# =============================================================================
# SIGNAL HANDLERS
# =============================================================================

handle_interrupt() {
    log "WARN" "Interrupt signal received"
    cleanup
    exit 130
}

handle_termination() {
    log "WARN" "Termination signal received"
    cleanup
    exit 143
}

trap handle_interrupt SIGINT
trap handle_termination SIGTERM

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    show_banner
    
    log "INFO" "Initializing Pentest-USB container..."
    log "INFO" "Service: $SERVICE_NAME"
    log "INFO" "Command: $*"
    
    # Initialization sequence
    check_environment
    setup_database
    setup_logging
    initialize_modules
    setup_security
    
    # Start health monitoring in background
    if [[ "${ENABLE_HEALTH_MONITOR:-true}" == "true" ]]; then
        start_health_monitor
    fi
    
    log "SUCCESS" "Container initialization completed"
    
    # Start the main service
    start_service "$@"
}

# =============================================================================
# SPECIAL COMMAND HANDLING
# =============================================================================

# Handle special commands
case "${1:-}" in
    health)
        health_check
        exit $?
        ;;
    test)
        log "INFO" "Running container tests..."
        cd "$PENTEST_HOME"
        python3 -m pytest tests/ -v
        exit $?
        ;;
    shell|bash)
        log "INFO" "Starting interactive shell..."
        exec /bin/bash
        ;;
    python)
        log "INFO" "Starting Python interpreter..."
        cd "$PENTEST_HOME"
        shift
        exec python3 "$@"
        ;;
    *)
        # Default: run main initialization and start service
        main "$@"
        ;;
esac