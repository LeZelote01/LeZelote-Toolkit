/**
 * WebSocket Client for Real-time Updates
 * =====================================
 * 
 * Handles real-time communication with the server
 */

(function() {
    'use strict';

    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 1000; // Start with 1 second

    /**
     * Initialize WebSocket connection
     */
    function initializeWebSocket() {
        if (typeof io === 'undefined') {
            console.error('Socket.IO not loaded');
            return;
        }

        // Connect to server
        socket = io({
            transports: ['websocket', 'polling'],
            upgrade: true,
            rememberUpgrade: true
        });

        // Connection event handlers
        socket.on('connect', handleConnect);
        socket.on('disconnect', handleDisconnect);
        socket.on('connect_error', handleConnectError);

        // System events
        socket.on('system_stats', handleSystemStats);
        socket.on('active_scans', handleActiveScans);

        // Scan events
        socket.on('scan_started', handleScanStarted);
        socket.on('scan_progress', handleScanProgress);
        socket.on('scan_completed', handleScanCompleted);
        socket.on('scan_failed', handleScanFailed);
        socket.on('scan_stopped', handleScanStopped);

        // Activity events
        socket.on('activity_update', handleActivityUpdate);

        console.log('WebSocket initialized');
    }

    /**
     * Handle successful connection
     */
    function handleConnect() {
        console.log('WebSocket connected');
        reconnectAttempts = 0;
        
        // Update connection status
        updateConnectionStatus(true);
        
        // Join user room for personalized updates
        if (typeof userId !== 'undefined') {
            socket.emit('join_user_room', { user_id: userId });
        }

        // Request initial data
        requestInitialData();

        PentestApp.ui.showToast('Connected to server', 'success', 3000);
    }

    /**
     * Handle disconnection
     */
    function handleDisconnect(reason) {
        console.log('WebSocket disconnected:', reason);
        
        // Update connection status
        updateConnectionStatus(false);

        if (reason === 'io server disconnect') {
            // Server initiated disconnect, don't reconnect
            PentestApp.ui.showToast('Disconnected from server', 'warning');
        } else {
            // Client disconnect or network issue, try to reconnect
            attemptReconnect();
        }
    }

    /**
     * Handle connection errors
     */
    function handleConnectError(error) {
        console.error('WebSocket connection error:', error);
        updateConnectionStatus(false);
        
        if (reconnectAttempts === 0) {
            PentestApp.ui.showToast('Connection failed, retrying...', 'error');
        }
        
        attemptReconnect();
    }

    /**
     * Attempt to reconnect
     */
    function attemptReconnect() {
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            const delay = reconnectDelay * Math.pow(2, reconnectAttempts - 1); // Exponential backoff
            
            console.log(`Reconnect attempt ${reconnectAttempts}/${maxReconnectAttempts} in ${delay}ms`);
            
            setTimeout(() => {
                if (socket && !socket.connected) {
                    socket.connect();
                }
            }, delay);
        } else {
            console.error('Max reconnection attempts reached');
            PentestApp.ui.showToast('Unable to connect to server. Please refresh the page.', 'error', 10000);
        }
    }

    /**
     * Update connection status indicator
     */
    function updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('systemStatus');
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${connected ? 'online' : 'offline'}`;
            statusIndicator.title = connected ? 'Connected' : 'Disconnected';
        }

        // Update navbar badge
        const navbarBadge = document.querySelector('.navbar .status-indicator');
        if (navbarBadge) {
            navbarBadge.className = `status-indicator ${connected ? 'online' : 'offline'}`;
        }
    }

    /**
     * Request initial data after connection
     */
    function requestInitialData() {
        // Request system stats
        fetch('/api/system/stats')
            .then(response => response.json())
            .then(data => handleSystemStats(data))
            .catch(error => console.error('Failed to fetch system stats:', error));

        // Request active scans
        fetch('/api/scans/active')
            .then(response => response.json())
            .then(data => handleActiveScans(data))
            .catch(error => console.error('Failed to fetch active scans:', error));
    }

    // ==========================================================================
    // Event Handlers
    // ==========================================================================

    /**
     * Handle system statistics update
     */
    function handleSystemStats(data) {
        if (!data) return;

        // Update CPU usage
        const cpuUsage = document.getElementById('cpuUsage');
        const cpuProgressBar = document.getElementById('cpuProgressBar');
        if (cpuUsage && data.cpu_percent !== undefined) {
            cpuUsage.textContent = Math.round(data.cpu_percent) + '%';
            if (cpuProgressBar) {
                PentestApp.ui.updateProgress(cpuProgressBar, data.cpu_percent);
            }
        }

        // Update Memory usage
        const memoryUsage = document.getElementById('memoryUsage');
        const memoryProgressBar = document.getElementById('memoryProgressBar');
        if (memoryUsage && data.memory_percent !== undefined) {
            memoryUsage.textContent = Math.round(data.memory_percent) + '%';
            if (memoryProgressBar) {
                PentestApp.ui.updateProgress(memoryProgressBar, data.memory_percent);
            }
        }

        // Update Disk usage
        const diskUsage = document.getElementById('diskUsage');
        const diskProgressBar = document.getElementById('diskProgressBar');
        if (diskUsage && data.disk_usage !== undefined) {
            diskUsage.textContent = Math.round(data.disk_usage) + '%';
            if (diskProgressBar) {
                PentestApp.ui.updateProgress(diskProgressBar, data.disk_usage);
            }
        }

        // Update active users
        const activeUsers = document.getElementById('activeUsers');
        if (activeUsers && data.connected_users !== undefined) {
            PentestApp.ui.updateCounter(activeUsers, data.connected_users);
        }

        // Update dashboard counters
        updateDashboardCounters(data);

        // Update performance chart if available
        if (typeof updatePerformanceChart === 'function') {
            updatePerformanceChart(data);
        }

        // Store stats in app state
        PentestApp.state.systemStats = data;
    }

    /**
     * Handle active scans update
     */
    function handleActiveScans(data) {
        if (!data) return;

        const activeScansBadge = document.getElementById('activeScansBadge');
        const activeScansCount = document.getElementById('activeScansCount');
        const activeScansList = document.getElementById('activeScansList');

        const scanCount = data.active_scans ? data.active_scans.length : data.count || 0;

        // Update badge
        if (activeScansBadge) {
            activeScansBadge.textContent = scanCount;
        }

        // Update counter
        if (activeScansCount) {
            PentestApp.ui.updateCounter(activeScansCount, scanCount);
        }

        // Update scans list
        if (activeScansList) {
            updateActiveScansList(data.active_scans || []);
        }

        // Store in app state
        PentestApp.state.activeScans = data.active_scans || {};
    }

    /**
     * Handle scan started event
     */
    function handleScanStarted(data) {
        console.log('Scan started:', data);
        
        PentestApp.ui.showToast(`Scan started on ${data.target}`, 'success');
        
        // Add to active scans list
        addToActiveScansList(data);
        
        // Update counters
        const activeScansCount = document.getElementById('activeScansCount');
        if (activeScansCount) {
            const currentCount = parseInt(activeScansCount.textContent) || 0;
            PentestApp.ui.updateCounter(activeScansCount, currentCount + 1);
        }
    }

    /**
     * Handle scan progress update
     */
    function handleScanProgress(data) {
        console.log('Scan progress:', data);
        
        // Update progress bar for this scan
        const progressBar = document.getElementById(`scan-progress-${data.scan_id}`);
        if (progressBar) {
            PentestApp.ui.updateProgress(progressBar, data.progress);
        }

        // Update status
        const statusElement = document.getElementById(`scan-status-${data.scan_id}`);
        if (statusElement) {
            statusElement.textContent = data.status || 'Running';
        }

        // Show periodic progress notifications (every 25%)
        if (data.progress && data.progress % 25 === 0 && data.progress < 100) {
            PentestApp.ui.showToast(`Scan ${data.scan_id}: ${data.progress}% complete`, 'info', 3000);
        }
    }

    /**
     * Handle scan completed event
     */
    function handleScanCompleted(data) {
        console.log('Scan completed:', data);
        
        PentestApp.ui.showToast(
            `Scan completed! Found ${data.vulnerabilities_count} vulnerabilities`, 
            'success'
        );
        
        // Remove from active scans
        removeFromActiveScansList(data.scan_id);
        
        // Update counters
        const completedScansCount = document.getElementById('completedScansCount');
        if (completedScansCount) {
            const currentCount = parseInt(completedScansCount.textContent) || 0;
            PentestApp.ui.updateCounter(completedScansCount, currentCount + 1);
        }

        const vulnerabilitiesCount = document.getElementById('vulnerabilitiesCount');
        if (vulnerabilitiesCount && data.vulnerabilities_count) {
            const currentCount = parseInt(vulnerabilitiesCount.textContent) || 0;
            PentestApp.ui.updateCounter(vulnerabilitiesCount, currentCount + data.vulnerabilities_count);
        }
    }

    /**
     * Handle scan failed event
     */
    function handleScanFailed(data) {
        console.log('Scan failed:', data);
        
        PentestApp.ui.showToast(`Scan failed: ${data.error}`, 'error');
        
        // Remove from active scans
        removeFromActiveScansList(data.scan_id);
    }

    /**
     * Handle scan stopped event
     */
    function handleScanStopped(data) {
        console.log('Scan stopped:', data);
        
        PentestApp.ui.showToast('Scan stopped by user', 'warning');
        
        // Remove from active scans
        removeFromActiveScansList(data.scan_id);
    }

    /**
     * Handle activity update
     */
    function handleActivityUpdate(data) {
        console.log('Activity update:', data);
        
        // Add to activity feed
        addToActivityFeed(data);
    }

    // ==========================================================================
    // UI Update Functions
    // ==========================================================================

    /**
     * Update dashboard counters
     */
    function updateDashboardCounters(data) {
        if (data.scans_completed !== undefined) {
            const element = document.getElementById('completedScansCount');
            if (element) {
                PentestApp.ui.updateCounter(element, data.scans_completed);
            }
        }

        if (data.vulnerabilities_found !== undefined) {
            const element = document.getElementById('vulnerabilitiesCount');
            if (element) {
                PentestApp.ui.updateCounter(element, data.vulnerabilities_found);
            }
        }
    }

    /**
     * Update active scans list
     */
    function updateActiveScansList(scans) {
        const activeScansList = document.getElementById('activeScansList');
        if (!activeScansList) return;

        if (scans.length === 0) {
            activeScansList.innerHTML = `
                <tr class="no-data">
                    <td colspan="5" class="text-center py-4">
                        <i class="fas fa-search fa-2x text-muted mb-3"></i>
                        <div class="text-muted">No active scans</div>
                        <button type="button" class="btn btn-sm btn-primary mt-2" data-bs-toggle="modal" data-bs-target="#newScanModal">
                            Start Your First Scan
                        </button>
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        scans.forEach(scan => {
            html += `
                <tr id="scan-row-${scan.id}">
                    <td>
                        <div class="fw-semibold">${PentestApp.utils.sanitizeHTML(scan.target)}</div>
                        <small class="text-muted">${scan.scan_type}</small>
                    </td>
                    <td><span class="badge bg-primary">${scan.scan_type}</span></td>
                    <td>
                        <div class="scan-progress">
                            <div class="progress mb-1">
                                <div class="progress-bar bg-primary" role="progressbar" 
                                     id="scan-progress-${scan.id}" 
                                     style="width: ${scan.progress || 0}%"></div>
                            </div>
                            <div class="progress-text">${Math.round(scan.progress || 0)}%</div>
                        </div>
                    </td>
                    <td>
                        <span class="scan-status status-${scan.status}" id="scan-status-${scan.id}">
                            ${scan.status || 'Running'}
                        </span>
                    </td>
                    <td>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="stopScan('${scan.id}')" title="Stop scan">
                            <i class="fas fa-stop"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="viewScanDetails('${scan.id}')" title="View details">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        activeScansList.innerHTML = html;
    }

    /**
     * Add scan to active scans list
     */
    function addToActiveScansList(scan) {
        const activeScansList = document.getElementById('activeScansList');
        if (!activeScansList) return;

        // Remove "no data" row if present
        const noDataRow = activeScansList.querySelector('.no-data');
        if (noDataRow) {
            noDataRow.remove();
        }

        const html = `
            <tr id="scan-row-${scan.id}">
                <td>
                    <div class="fw-semibold">${PentestApp.utils.sanitizeHTML(scan.target)}</div>
                    <small class="text-muted">${scan.scan_type || 'Unknown'}</small>
                </td>
                <td><span class="badge bg-primary">${scan.scan_type || 'Unknown'}</span></td>
                <td>
                    <div class="scan-progress">
                        <div class="progress mb-1">
                            <div class="progress-bar bg-primary" role="progressbar" 
                                 id="scan-progress-${scan.id}" 
                                 style="width: ${scan.progress || 0}%"></div>
                        </div>
                        <div class="progress-text">${Math.round(scan.progress || 0)}%</div>
                    </div>
                </td>
                <td>
                    <span class="scan-status status-${scan.status || 'starting'}" id="scan-status-${scan.id}">
                        ${scan.status || 'Starting'}
                    </span>
                </td>
                <td>
                    <button type="button" class="btn btn-sm btn-outline-danger" 
                            onclick="stopScan('${scan.id}')" title="Stop scan">
                        <i class="fas fa-stop"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-primary" 
                            onclick="viewScanDetails('${scan.id}')" title="View details">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;

        activeScansList.insertAdjacentHTML('afterbegin', html);
    }

    /**
     * Remove scan from active scans list
     */
    function removeFromActiveScansList(scanId) {
        const scanRow = document.getElementById(`scan-row-${scanId}`);
        if (scanRow) {
            scanRow.remove();
        }

        // Update active scans counter
        const activeScansCount = document.getElementById('activeScansCount');
        if (activeScansCount) {
            const currentCount = parseInt(activeScansCount.textContent) || 0;
            PentestApp.ui.updateCounter(activeScansCount, Math.max(0, currentCount - 1));
        }

        // Check if we need to show "no data" message
        const activeScansList = document.getElementById('activeScansList');
        if (activeScansList && activeScansList.children.length === 0) {
            activeScansList.innerHTML = `
                <tr class="no-data">
                    <td colspan="5" class="text-center py-4">
                        <i class="fas fa-search fa-2x text-muted mb-3"></i>
                        <div class="text-muted">No active scans</div>
                        <button type="button" class="btn btn-sm btn-primary mt-2" data-bs-toggle="modal" data-bs-target="#newScanModal">
                            Start Your First Scan
                        </button>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * Add item to activity feed
     */
    function addToActivityFeed(activity) {
        const activityFeed = document.getElementById('activityFeed');
        if (!activityFeed) return;

        const iconClass = getActivityIcon(activity.type);
        const bgClass = getActivityBgClass(activity.type);

        const html = `
            <div class="activity-item">
                <div class="activity-icon bg-${bgClass}">
                    <i class="fas fa-${iconClass}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${PentestApp.utils.sanitizeHTML(activity.title)}</div>
                    <div class="activity-description">${PentestApp.utils.sanitizeHTML(activity.description)}</div>
                    <div class="activity-time">${PentestApp.utils.formatRelativeTime(activity.timestamp)}</div>
                </div>
            </div>
        `;

        activityFeed.insertAdjacentHTML('afterbegin', html);

        // Keep only last 10 items
        const items = activityFeed.querySelectorAll('.activity-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }

    /**
     * Get activity icon based on type
     */
    function getActivityIcon(type) {
        const icons = {
            'scan_started': 'play',
            'scan_completed': 'check',
            'scan_failed': 'times',
            'vulnerability_found': 'exclamation-triangle',
            'report_generated': 'file-alt',
            'user_login': 'sign-in-alt',
            'user_logout': 'sign-out-alt'
        };
        return icons[type] || 'info';
    }

    /**
     * Get activity background class based on type
     */
    function getActivityBgClass(type) {
        const classes = {
            'scan_started': 'primary',
            'scan_completed': 'success',
            'scan_failed': 'danger',
            'vulnerability_found': 'warning',
            'report_generated': 'info',
            'user_login': 'success',
            'user_logout': 'secondary'
        };
        return classes[type] || 'secondary';
    }

    // ==========================================================================
    // Global Functions
    // ==========================================================================

    /**
     * Join scan room for real-time updates
     */
    function joinScanRoom(scanId) {
        if (socket && socket.connected) {
            socket.emit('join_scan_room', { scan_id: scanId });
        }
    }

    /**
     * Leave scan room
     */
    function leaveScanRoom(scanId) {
        if (socket && socket.connected) {
            socket.emit('leave_scan_room', { scan_id: scanId });
        }
    }

    /**
     * Stop a scan
     */
    function stopScan(scanId) {
        PentestApp.ui.showConfirm(
            'Are you sure you want to stop this scan?',
            function() {
                PentestApp.api.stopScan(scanId)
                    .then(response => {
                        if (response.success) {
                            PentestApp.ui.showToast('Scan stopped successfully', 'success');
                        } else {
                            PentestApp.ui.showToast(response.message || 'Failed to stop scan', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Stop scan error:', error);
                        PentestApp.ui.showToast('Failed to stop scan', 'error');
                    });
            }
        );
    }

    /**
     * View scan details
     */
    function viewScanDetails(scanId) {
        window.location.href = `/scan/monitor/${scanId}`;
    }

    // ==========================================================================
    // Export functions
    // ==========================================================================

    // Make functions globally available
    window.initializeWebSocket = initializeWebSocket;
    window.joinScanRoom = joinScanRoom;
    window.leaveScanRoom = leaveScanRoom;
    window.stopScan = stopScan;
    window.viewScanDetails = viewScanDetails;

    // Store socket reference globally
    window.PentestApp = window.PentestApp || {};
    window.PentestApp.socket = socket;

})();