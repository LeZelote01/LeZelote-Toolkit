#!/bin/bash

# =============================================================================
# PENTEST-USB TOOLKIT - DOCKER STARTUP SCRIPT
# =============================================================================
# Automated startup and health monitoring for containerized environment
# Supports multiple deployment strategies and system configurations
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURATION & GLOBALS
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CONTAINERS_CONFIG="${SCRIPT_DIR}/containers.json"
DOCKER_COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_MODE="${DEPLOYMENT_MODE:-standard}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-300}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-10}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
RESTART_ON_FAILURE="${RESTART_ON_FAILURE:-true}"

# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        ERROR)   echo -e "${RED}[${timestamp}] [ERROR] ${message}${NC}" ;;
        WARN)    echo -e "${YELLOW}[${timestamp}] [WARN] ${message}${NC}" ;;
        INFO)    echo -e "${GREEN}[${timestamp}] [INFO] ${message}${NC}" ;;
        DEBUG)   [[ "$LOG_LEVEL" == "DEBUG" ]] && echo -e "${BLUE}[${timestamp}] [DEBUG] ${message}${NC}" ;;
        SUCCESS) echo -e "${CYAN}[${timestamp}] [SUCCESS] ${message}${NC}" ;;
        *)       echo -e "[${timestamp}] ${message}" ;;
    esac
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

show_banner() {
    cat << 'EOF'
 ____            _            _     _   _ ____  ____  
|  _ \ ___ _ __ | |_ ___  ___| |_  | | | / ___|| __ ) 
| |_) / _ \ '_ \| __/ _ \/ __| __| | | | \___ \|  _ \ 
|  __/  __/ | | | ||  __/\__ \ |_  | |_| |___) | |_) |
|_|   \___|_| |_|\__\___||___/\__|  \___/|____/|____/ 
                                                      
═══════════════════════════════════════════════════════
    Portable Penetration Testing Toolkit v1.0.0
    Docker Container Orchestration System
═══════════════════════════════════════════════════════
EOF
}

check_prerequisites() {
    log "INFO" "Checking system prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log "ERROR" "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log "ERROR" "Docker daemon is not running"
        exit 1
    fi
    
    # Check system resources
    local total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    local cpu_cores=$(nproc)
    
    log "INFO" "System Resources: ${cpu_cores} CPU cores, ${total_mem}GB RAM"
    
    # Memory requirements check
    case "$DEPLOYMENT_MODE" in
        minimal)     MIN_MEM=4 ;;
        standard)    MIN_MEM=8 ;;
        comprehensive) MIN_MEM=16 ;;
        enterprise)  MIN_MEM=32 ;;
        *)           MIN_MEM=8 ;;
    esac
    
    if [[ $total_mem -lt $MIN_MEM ]]; then
        log "WARN" "Insufficient memory for $DEPLOYMENT_MODE mode (${total_mem}GB < ${MIN_MEM}GB)"
        log "WARN" "Consider using a lighter deployment mode"
    fi
    
    log "SUCCESS" "Prerequisites check completed"
}

check_configuration() {
    log "INFO" "Validating configuration files..."
    
    # Check Docker Compose file
    if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
        log "ERROR" "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    # Check containers configuration
    if [[ ! -f "$CONTAINERS_CONFIG" ]]; then
        log "ERROR" "Containers configuration not found: $CONTAINERS_CONFIG"
        exit 1
    fi
    
    # Validate Docker Compose syntax
    if ! docker-compose -f "$DOCKER_COMPOSE_FILE" config &> /dev/null; then
        log "ERROR" "Invalid Docker Compose configuration"
        exit 1
    fi
    
    log "SUCCESS" "Configuration validation completed"
}

setup_environment() {
    log "INFO" "Setting up environment..."
    
    # Create necessary directories
    local dirs=(
        "${PROJECT_ROOT}/logs/docker"
        "${PROJECT_ROOT}/outputs/docker"
        "${PROJECT_ROOT}/data/docker"
        "/tmp/pentest-docker"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log "DEBUG" "Created directory: $dir"
    done
    
    # Set environment variables
    export COMPOSE_PROJECT_NAME="pentest-usb"
    export COMPOSE_FILE="$DOCKER_COMPOSE_FILE"
    export PENTEST_DATA_PATH="${PROJECT_ROOT}/data"
    export PENTEST_LOGS_PATH="${PROJECT_ROOT}/logs"
    export PENTEST_OUTPUTS_PATH="${PROJECT_ROOT}/outputs"
    
    # Load deployment-specific environment
    case "$DEPLOYMENT_MODE" in
        minimal)
            export COMPOSE_PROFILES=""
            ;;
        standard)
            export COMPOSE_PROFILES="scanning"
            ;;
        comprehensive)
            export COMPOSE_PROFILES="scanning,premium,tools"
            ;;
        enterprise)
            export COMPOSE_PROFILES="all"
            ;;
    esac
    
    log "SUCCESS" "Environment setup completed (Mode: $DEPLOYMENT_MODE)"
}

pull_images() {
    log "INFO" "Pulling required Docker images..."
    
    # Get list of services based on deployment mode
    local services
    case "$DEPLOYMENT_MODE" in
        minimal)
            services="pentest-orchestrator postgresql redis"
            ;;
        standard)
            services="pentest-orchestrator postgresql redis zaproxy nuclei metasploit"
            ;;
        comprehensive)
            services="pentest-orchestrator postgresql redis nessus openvas zaproxy burpsuite metasploit bloodhound kali-tools"
            ;;
        enterprise)
            services="" # All services
            ;;
    esac
    
    if [[ -n "$services" ]]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" pull $services
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    fi
    
    log "SUCCESS" "Image pull completed"
}

build_custom_images() {
    log "INFO" "Building custom images..."
    
    # Build base image
    docker build \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        -t pentest-usb:base \
        -f "${SCRIPT_DIR}/Dockerfile.base" \
        "$PROJECT_ROOT"
    
    # Build tool-specific images based on deployment mode
    local containers_to_build
    case "$DEPLOYMENT_MODE" in
        minimal)
            containers_to_build=""
            ;;
        standard)
            containers_to_build="zaproxy nuclei metasploit"
            ;;
        comprehensive)
            containers_to_build="nessus openvas zaproxy burpsuite metasploit bloodhound kali-tools"
            ;;
        enterprise)
            containers_to_build="nessus openvas zaproxy burpsuite metasploit bloodhound kali-tools"
            ;;
    esac
    
    for container in $containers_to_build; do
        log "INFO" "Building $container container..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" build "$container"
    done
    
    log "SUCCESS" "Custom image build completed"
}

start_services() {
    log "INFO" "Starting services in $DEPLOYMENT_MODE mode..."
    
    local compose_cmd="docker-compose -f $DOCKER_COMPOSE_FILE"
    
    # Add profiles for comprehensive modes
    if [[ "$DEPLOYMENT_MODE" != "minimal" ]]; then
        compose_cmd="$compose_cmd --profile $COMPOSE_PROFILES"
    fi
    
    # Start services based on deployment mode
    case "$DEPLOYMENT_MODE" in
        minimal)
            $compose_cmd up -d pentest-orchestrator postgresql redis
            ;;
        standard)
            $compose_cmd up -d
            ;;
        comprehensive|enterprise)
            $compose_cmd up -d
            ;;
    esac
    
    log "SUCCESS" "Services startup initiated"
}

wait_for_health() {
    log "INFO" "Waiting for services to become healthy..."
    
    local start_time=$(date +%s)
    local services=(
        "pentest_orchestrator:8080"
        "pentest_postgresql:5432"
        "pentest_redis:6379"
    )
    
    # Add mode-specific services
    case "$DEPLOYMENT_MODE" in
        standard|comprehensive|enterprise)
            services+=("pentest_zap:8082")
            services+=("pentest_metasploit:55553")
            ;;
    esac
    
    case "$DEPLOYMENT_MODE" in
        comprehensive|enterprise)
            services+=("pentest_nessus:8834")
            services+=("pentest_bloodhound:7474")
            ;;
    esac
    
    for service_port in "${services[@]}"; do
        local container_name="${service_port%:*}"
        local port="${service_port#*:}"
        
        log "INFO" "Checking health of $container_name on port $port..."
        
        local attempts=0
        local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
        
        while [[ $attempts -lt $max_attempts ]]; do
            if docker exec "$container_name" netstat -tln | grep -q ":$port "; then
                log "SUCCESS" "$container_name is healthy"
                break
            fi
            
            attempts=$((attempts + 1))
            sleep "$HEALTH_CHECK_INTERVAL"
            
            local elapsed=$(($(date +%s) - start_time))
            log "DEBUG" "Health check attempt $attempts/$max_attempts for $container_name (${elapsed}s elapsed)"
        done
        
        if [[ $attempts -eq $max_attempts ]]; then
            log "ERROR" "Health check failed for $container_name after ${HEALTH_CHECK_TIMEOUT}s"
            return 1
        fi
    done
    
    log "SUCCESS" "All services are healthy"
}

show_status() {
    log "INFO" "Service Status Summary:"
    echo
    
    # Show running containers
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    echo
    
    # Show service URLs
    cat << EOF
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE ACCESS URLS                     │
├─────────────────────────────────────────────────────────────┤
│ Main Interface:     http://localhost:8080                  │
│ API Interface:      http://localhost:8081                  │
│ PostgreSQL:         postgresql://localhost:5432/pentest_usb │
│ Redis:              redis://localhost:6379                 │
EOF

    # Show mode-specific URLs
    case "$DEPLOYMENT_MODE" in
        standard|comprehensive|enterprise)
            cat << EOF
│ OWASP ZAP:          http://localhost:8082                  │
│ Metasploit RPC:     https://localhost:55553                │
EOF
            ;;
    esac
    
    case "$DEPLOYMENT_MODE" in
        comprehensive|enterprise)
            cat << EOF
│ Nessus:             https://localhost:8834                 │
│ BloodHound:         http://localhost:3000                  │
│ Neo4j Browser:      http://localhost:7474                  │
EOF
            ;;
    esac
    
    case "$DEPLOYMENT_MODE" in
        enterprise)
            cat << EOF
│ Kibana:             http://localhost:5601                  │
│ Elasticsearch:      http://localhost:9200                  │
│ VNC Web:            http://localhost:6901                  │
│ File Transfer:      http://localhost:8085                  │
EOF
            ;;
    esac
    
    echo "└─────────────────────────────────────────────────────────────┘"
    echo
}

setup_monitoring() {
    log "INFO" "Setting up health monitoring..."
    
    # Create monitoring script
    cat > "/tmp/pentest-docker/health-monitor.sh" << 'EOF'
#!/bin/bash
while true; do
    if ! docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
        echo "$(date): Some services are down, attempting restart..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    fi
    sleep 60
done
EOF
    
    chmod +x "/tmp/pentest-docker/health-monitor.sh"
    
    if [[ "$RESTART_ON_FAILURE" == "true" ]]; then
        nohup "/tmp/pentest-docker/health-monitor.sh" > "/tmp/pentest-docker/monitor.log" 2>&1 &
        echo $! > "/tmp/pentest-docker/monitor.pid"
        log "INFO" "Health monitoring started (PID: $(cat /tmp/pentest-docker/monitor.pid))"
    fi
}

cleanup() {
    log "INFO" "Cleaning up..."
    
    # Stop monitoring if running
    if [[ -f "/tmp/pentest-docker/monitor.pid" ]]; then
        local monitor_pid=$(cat "/tmp/pentest-docker/monitor.pid")
        if kill "$monitor_pid" 2>/dev/null; then
            log "INFO" "Health monitor stopped"
        fi
        rm -f "/tmp/pentest-docker/monitor.pid"
    fi
    
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
    
    log "INFO" "Starting Pentest-USB Docker environment..."
    log "INFO" "Deployment Mode: $DEPLOYMENT_MODE"
    
    check_prerequisites
    check_configuration
    setup_environment
    
    # Build and start based on deployment strategy
    if [[ "${BUILD_IMAGES:-true}" == "true" ]]; then
        build_custom_images
    fi
    
    if [[ "${PULL_IMAGES:-true}" == "true" ]]; then
        pull_images
    fi
    
    start_services
    wait_for_health
    setup_monitoring
    show_status
    
    log "SUCCESS" "Pentest-USB Docker environment is ready!"
    log "INFO" "Use 'docker-compose -f $DOCKER_COMPOSE_FILE logs -f' to view logs"
    log "INFO" "Use 'docker-compose -f $DOCKER_COMPOSE_FILE down' to stop all services"
    
    # Keep script running if in foreground mode
    if [[ "${FOREGROUND:-false}" == "true" ]]; then
        log "INFO" "Running in foreground mode. Press Ctrl+C to stop."
        while true; do
            sleep 30
            # Check if core services are still running
            if ! docker inspect pentest_orchestrator &>/dev/null; then
                log "ERROR" "Core orchestrator container stopped unexpectedly"
                exit 1
            fi
        done
    fi
}

# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

usage() {
    cat << EOF
Usage: $0 [OPTIONS] [COMMAND]

COMMANDS:
    start           Start the Docker environment (default)
    stop            Stop all services
    restart         Restart all services
    status          Show service status
    logs            Show logs for all services
    cleanup         Stop services and remove volumes
    update          Update images and restart

OPTIONS:
    -m, --mode MODE         Deployment mode: minimal|standard|comprehensive|enterprise
    -f, --foreground        Run in foreground mode
    -h, --help             Show this help message
    --no-build             Skip building custom images
    --no-pull              Skip pulling images
    --no-monitor           Disable health monitoring

ENVIRONMENT VARIABLES:
    DEPLOYMENT_MODE         Deployment strategy (default: standard)
    HEALTH_CHECK_TIMEOUT    Health check timeout in seconds (default: 300)
    LOG_LEVEL              Logging level: DEBUG|INFO|WARN|ERROR (default: INFO)
    RESTART_ON_FAILURE     Auto-restart failed services (default: true)

EXAMPLES:
    $0 --mode comprehensive --foreground
    $0 stop
    $0 logs
    DEPLOYMENT_MODE=minimal $0 start
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            DEPLOYMENT_MODE="$2"
            shift 2
            ;;
        -f|--foreground)
            FOREGROUND="true"
            shift
            ;;
        --no-build)
            BUILD_IMAGES="false"
            shift
            ;;
        --no-pull)
            PULL_IMAGES="false"
            shift
            ;;
        --no-monitor)
            RESTART_ON_FAILURE="false"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        start)
            COMMAND="start"
            shift
            ;;
        stop)
            COMMAND="stop"
            shift
            ;;
        restart)
            COMMAND="restart"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        logs)
            COMMAND="logs"
            shift
            ;;
        cleanup)
            COMMAND="cleanup"
            shift
            ;;
        update)
            COMMAND="update"
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Execute command
case "${COMMAND:-start}" in
    start)
        main
        ;;
    stop)
        log "INFO" "Stopping all services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        cleanup
        ;;
    restart)
        log "INFO" "Restarting all services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" restart
        ;;
    status)
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
        ;;
    logs)
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
        ;;
    cleanup)
        log "INFO" "Cleaning up all services and data..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
        docker system prune -f
        cleanup
        ;;
    update)
        log "INFO" "Updating images and restarting..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" pull
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
        ;;
esac