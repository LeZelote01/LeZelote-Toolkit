/*
 * WebSocket Connection Handler for Pentest-USB Toolkit
 * ===================================================
 */

// WebSocket connection management
let socket = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let reconnectInterval = 5000; // 5 seconds

/**
 * Initialize WebSocket connection
 */
function initializeWebSocket() {
    if (!window.PentestApp) {
        console.error('PentestApp not initialized');
        return;
    }
    
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}${window.PentestApp.config.wsNamespace}`;
        
        console.log('Connecting to WebSocket:', wsUrl);
        
        socket = io(wsUrl, {
            transports: ['websocket', 'polling'],
            upgrade: true,
            rememberUpgrade: true
        });
        
        setupWebSocketHandlers();
        window.PentestApp.socket = socket;
        
    } catch (error) {
        console.error('WebSocket initialization failed:', error);
    }
}

/**
 * Setup WebSocket event handlers
 */
function setupWebSocketHandlers() {
    if (!socket) return;
    
    // Connection events
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('connect_error', handleConnectError);
    socket.on('reconnect', handleReconnect);
    socket.on('reconnect_error', handleReconnectError);
    
    // Application events
    socket.on('system_stats', handleSystemStats);
    socket.on('active_scans', handleActiveScans);
    socket.on('scan_started', handleScanStarted);
    socket.on('scan_progress', handleScanProgress);
    socket.on('scan_completed', handleScanCompleted);
    socket.on('scan_failed', handleScanFailed);
    socket.on('scan_stopped', handleScanStopped);
    socket.on('vulnerability_found', handleVulnerabilityFound);
    socket.on('notification', handleNotification);
    socket.on('user_message', handleUserMessage);
    socket.on('system_alert', handleSystemAlert);
}

/**
 * Handle successful connection
 */
function handleConnect() {
    console.log('WebSocket connected successfully');
    reconnectAttempts = 0;
    
    // Update connection status indicator
    updateConnectionStatus(true);
    
    // Join user-specific room if authenticated
    if (window.PentestApp.state.currentUser) {
        socket.emit('join_user_room', {
            user_id: window.PentestApp.state.currentUser.user_id
        });
    }
    
    // Show connection success notification
    showToast('Connected to real-time updates', 'success', 3000);
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('websocketConnected'));
}

/**
 * Handle disconnection
 */
function handleDisconnect(reason) {
    console.log('WebSocket disconnected:', reason);
    
    // Update connection status indicator
    updateConnectionStatus(false);
    
    // Show disconnection notification
    if (reason !== 'io client disconnect') {
        showToast('Connection lost. Attempting to reconnect...', 'warning', 5000);
    }
    
    // Attempt reconnection for certain disconnect reasons
    if (reason === 'io server disconnect' || reason === 'transport close') {
        attemptReconnection();
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('websocketDisconnected', { detail: { reason } }));
}

/**
 * Handle connection errors
 */
function handleConnectError(error) {
    console.error('WebSocket connection error:', error);
    
    reconnectAttempts++;
    
    if (reconnectAttempts < maxReconnectAttempts) {
        setTimeout(() => {
            console.log(`Reconnection attempt ${reconnectAttempts}/${maxReconnectAttempts}`);
            socket.connect();
        }, reconnectInterval * reconnectAttempts);
    } else {
        showToast('Unable to establish real-time connection. Some features may be limited.', 'error', 10000);
        updateConnectionStatus(false);
    }
}

/**
 * Handle successful reconnection
 */
function handleReconnect(attemptNumber) {
    console.log('WebSocket reconnected after', attemptNumber, 'attempts');
    reconnectAttempts = 0;
    updateConnectionStatus(true);
    showToast('Reconnected to real-time updates', 'success', 3000);
}

/**
 * Handle reconnection errors
 */
function handleReconnectError(error) {
    console.error('WebSocket reconnection error:', error);
}

/**
 * Handle system statistics updates
 */
function handleSystemStats(data) {
    console.log('Received system stats:', data);
    
    // Update global state
    if (window.PentestApp) {
        window.PentestApp.state.systemStats = data;
    }
    
    // Update UI elements
    if (typeof updateSystemMetrics === 'function') {
        updateSystemMetrics(data);
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('systemStatsReceived', { detail: data }));
}

/**
 * Handle active scans updates
 */
function handleActiveScans(scans) {
    console.log('Received active scans:', scans);
    
    // Update global state
    if (window.PentestApp) {
        window.PentestApp.state.activeScans = scans;
    }
    
    // Update UI elements
    if (typeof updateActiveScansList === 'function') {
        updateActiveScansList(scans);
    }
    
    // Update badges
    if (typeof updateActiveScansBadge === 'function') {
        updateActiveScansBadge(scans.length);
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('activeScansReceived', { detail: scans }));
}

/**
 * Handle scan started event
 */
function handleScanStarted(data) {
    console.log('Scan started:', data);
    
    // Show notification
    showToast(`Scan started on ${data.target}`, 'info', 5000);
    
    // Add to active scans list
    if (window.PentestApp && window.PentestApp.state.activeScans) {
        window.PentestApp.state.activeScans.push(data);
    }
    
    // Update UI
    refreshActiveScansDisplay();
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('scanStarted', { detail: data }));
}

/**
 * Handle scan progress updates
 */
function handleScanProgress(data) {
    console.log('Scan progress:', data);
    
    // Update progress in UI
    updateScanProgress(data.scan_id, data.progress, data.status, data.message);
    
    // Update active scans state
    if (window.PentestApp && window.PentestApp.state.activeScans) {
        const scanIndex = window.PentestApp.state.activeScans.findIndex(s => s.id === data.scan_id);
        if (scanIndex !== -1) {
            window.PentestApp.state.activeScans[scanIndex].progress = data.progress;
            window.PentestApp.state.activeScans[scanIndex].status = data.status;
        }
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('scanProgress', { detail: data }));
}

/**
 * Handle scan completion
 */
function handleScanCompleted(data) {
    console.log('Scan completed:', data);
    
    // Show completion notification with details
    const message = `Scan completed! Found ${data.vulnerabilities_count} vulnerabilities in ${data.duration}`;
    showToast(message, 'success', 8000);
    
    // Remove from active scans
    if (window.PentestApp && window.PentestApp.state.activeScans) {
        window.PentestApp.state.activeScans = window.PentestApp.state.activeScans.filter(s => s.id !== data.scan_id);
    }
    
    // Update UI
    refreshActiveScansDisplay();
    markScanCompleted(data.scan_id, data);
    
    // Browser notification for important scans
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Scan Completed', {
            body: message,
            icon: '/static/img/logo.png',
            tag: `scan-completed-${data.scan_id}`
        });
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('scanCompleted', { detail: data }));
}

/**
 * Handle scan failure
 */
function handleScanFailed(data) {
    console.log('Scan failed:', data);
    
    // Show failure notification
    showToast(`Scan failed: ${data.error}`, 'error', 10000);
    
    // Update scan status in UI
    markScanFailed(data.scan_id, data.error);
    
    // Remove from active scans
    if (window.PentestApp && window.PentestApp.state.activeScans) {
        window.PentestApp.state.activeScans = window.PentestApp.state.activeScans.filter(s => s.id !== data.scan_id);
    }
    
    // Update UI
    refreshActiveScansDisplay();
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('scanFailed', { detail: data }));
}

/**
 * Handle scan stopped
 */
function handleScanStopped(data) {
    console.log('Scan stopped:', data);
    
    // Show stopped notification
    showToast('Scan stopped by user', 'warning', 5000);
    
    // Remove from active scans
    if (window.PentestApp && window.PentestApp.state.activeScans) {
        window.PentestApp.state.activeScans = window.PentestApp.state.activeScans.filter(s => s.id !== data.scan_id);
    }
    
    // Update UI
    refreshActiveScansDisplay();
    markScanStopped(data.scan_id);
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('scanStopped', { detail: data }));
}

/**
 * Handle vulnerability discovery
 */
function handleVulnerabilityFound(data) {
    console.log('Vulnerability found:', data);
    
    // Show vulnerability notification based on severity
    const severityColors = {
        'critical': 'error',
        'high': 'warning',
        'medium': 'info',
        'low': 'info'
    };
    
    const color = severityColors[data.severity] || 'info';
    const message = `${data.severity.toUpperCase()}: ${data.title}`;
    
    showToast(message, color, 8000);
    
    // Browser notification for high severity vulnerabilities
    if (['critical', 'high'].includes(data.severity) && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('Vulnerability Found', {
            body: message,
            icon: '/static/img/logo.png',
            tag: `vuln-${data.id}`
        });
    }
    
    // Update vulnerability counters
    updateVulnerabilityCounters(data.severity);
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('vulnerabilityFound', { detail: data }));
}

/**
 * Handle general notifications
 */
function handleNotification(data) {
    console.log('Notification received:', data);
    
    // Show toast notification
    showToast(data.message, data.type || 'info', data.duration || 5000);
    
    // Add to notifications list
    if (window.PentestApp && window.PentestApp.state.notifications) {
        window.PentestApp.state.notifications.unshift(data);
    }
    
    // Update notifications UI
    if (typeof updateNotificationsDisplay === 'function') {
        updateNotificationsDisplay();
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('notificationReceived', { detail: data }));
}

/**
 * Handle user-specific messages
 */
function handleUserMessage(data) {
    console.log('User message received:', data);
    
    // Show message based on type
    if (data.type === 'alert') {
        showToast(data.message, 'warning', 8000);
    } else if (data.type === 'info') {
        showToast(data.message, 'info', 5000);
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('userMessage', { detail: data }));
}

/**
 * Handle system alerts
 */
function handleSystemAlert(data) {
    console.log('System alert received:', data);
    
    // Show system alert
    showToast(`System Alert: ${data.message}`, 'error', 10000);
    
    // Browser notification for system alerts
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('System Alert', {
            body: data.message,
            icon: '/static/img/logo.png',
            tag: 'system-alert'
        });
    }
    
    // Trigger custom event
    document.dispatchEvent(new CustomEvent('systemAlert', { detail: data }));
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('systemStatus');
    if (indicator) {
        indicator.className = `status-indicator ${connected ? 'online' : 'offline'}`;
        indicator.title = connected ? 'System Online' : 'System Offline';
    }
    
    // Update global state
    if (window.PentestApp) {
        window.PentestApp.state.connected = connected;
    }
}

/**
 * Emit WebSocket event
 */
function emitSocketEvent(event, data) {
    if (socket && socket.connected) {
        socket.emit(event, data);
        return true;
    } else {
        console.warn('WebSocket not connected. Cannot emit event:', event);
        return false;
    }
}

/**
 * Join scan room for real-time updates
 */
function joinScanRoom(scanId) {
    return emitSocketEvent('join_scan_room', { scan_id: scanId });
}

/**
 * Leave scan room
 */
function leaveScanRoom(scanId) {
    return emitSocketEvent('leave_scan_room', { scan_id: scanId });
}

/**
 * Request system stats update
 */
function requestSystemStats() {
    return emitSocketEvent('request_system_stats', {});
}

/**
 * Request active scans update
 */
function requestActiveScans() {
    return emitSocketEvent('request_active_scans', {});
}

/**
 * Attempt manual reconnection
 */
function attemptReconnection() {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.log('Maximum reconnection attempts reached');
        return;
    }
    
    setTimeout(() => {
        if (socket && !socket.connected) {
            console.log('Attempting manual reconnection...');
            socket.connect();
        }
    }, reconnectInterval);
}

/**
 * Disconnect WebSocket
 */
function disconnectWebSocket() {
    if (socket) {
        socket.disconnect();
        socket = null;
        window.PentestApp.socket = null;
        updateConnectionStatus(false);
    }
}

/**
 * Get WebSocket connection status
 */
function getConnectionStatus() {
    return socket ? socket.connected : false;
}

// Helper functions for UI updates (implement as needed per page)
function refreshActiveScansDisplay() {
    if (typeof updateActiveScans === 'function') {
        updateActiveScans();
    }
}

function updateScanProgress(scanId, progress, status, message) {
    // Update progress bars and status displays
    const progressBar = document.querySelector(`[data-scan-id="${scanId}"] .progress-bar`);
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${progress}%`;
    }
    
    const statusBadge = document.querySelector(`[data-scan-id="${scanId}"] .status-badge`);
    if (statusBadge) {
        statusBadge.textContent = status;
        statusBadge.className = `badge ${getStatusBadgeClass(status)} status-badge`;
    }
    
    // Update scan logs if present
    const logsContainer = document.querySelector(`[data-scan-id="${scanId}"] .scan-logs`);
    if (logsContainer && message) {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="log-time">${new Date().toLocaleTimeString()}</span>
            <span class="log-message">${escapeHtml(message)}</span>
        `;
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

function markScanCompleted(scanId, data) {
    const scanRow = document.querySelector(`[data-scan-id="${scanId}"]`);
    if (scanRow) {
        scanRow.classList.add('scan-completed');
        
        // Update status
        const statusBadge = scanRow.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.textContent = 'completed';
            statusBadge.className = 'badge bg-success status-badge';
        }
        
        // Update progress
        const progressBar = scanRow.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.className = 'progress-bar bg-success';
            progressBar.textContent = '100%';
        }
    }
}

function markScanFailed(scanId, error) {
    const scanRow = document.querySelector(`[data-scan-id="${scanId}"]`);
    if (scanRow) {
        scanRow.classList.add('scan-failed');
        
        // Update status
        const statusBadge = scanRow.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.textContent = 'failed';
            statusBadge.className = 'badge bg-danger status-badge';
            statusBadge.title = error;
        }
    }
}

function markScanStopped(scanId) {
    const scanRow = document.querySelector(`[data-scan-id="${scanId}"]`);
    if (scanRow) {
        scanRow.classList.add('scan-stopped');
        
        // Update status
        const statusBadge = scanRow.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.textContent = 'stopped';
            statusBadge.className = 'badge bg-warning status-badge';
        }
    }
}

function updateVulnerabilityCounters(severity) {
    const counter = document.getElementById(`${severity}Count`);
    if (counter) {
        const currentCount = parseInt(counter.textContent) || 0;
        counter.textContent = currentCount + 1;
    }
    
    // Update total vulnerabilities
    const totalCounter = document.getElementById('vulnerabilitiesCount');
    if (totalCounter) {
        const currentTotal = parseInt(totalCounter.textContent) || 0;
        totalCounter.textContent = currentTotal + 1;
    }
}

// Expose functions globally
window.WebSocket = {
    initialize: initializeWebSocket,
    disconnect: disconnectWebSocket,
    emit: emitSocketEvent,
    joinScanRoom: joinScanRoom,
    leaveScanRoom: leaveScanRoom,
    requestSystemStats: requestSystemStats,
    requestActiveScans: requestActiveScans,
    getStatus: getConnectionStatus
};

// Auto-initialize WebSocket when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeWebSocket);
} else {
    initializeWebSocket();
}