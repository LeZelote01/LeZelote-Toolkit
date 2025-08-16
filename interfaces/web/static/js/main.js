/*
 * Main JavaScript for Pentest-USB Toolkit Web Interface
 * =====================================================
 */

// Global application state
window.PentestApp = {
    socket: null,
    charts: {},
    config: {
        apiBaseUrl: '/api',
        wsNamespace: '/',
        refreshInterval: 30000,
        chartColors: {
            primary: '#007bff',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8'
        }
    },
    state: {
        activeScans: [],
        systemStats: {},
        notifications: [],
        currentUser: null
    }
};

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Pentest-USB Toolkit...');
    
    // Initialize core components
    initializeApplication();
    
    // Setup global event listeners
    setupGlobalEventListeners();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Load initial data
    loadInitialData();
    
    console.log('Application initialized successfully');
});

/**
 * Initialize core application components
 */
function initializeApplication() {
    // Set up CSRF token for AJAX requests
    setupCSRFToken();
    
    // Initialize notification system
    initializeNotifications();
    
    // Setup periodic data refresh
    setupPeriodicRefresh();
    
    // Initialize theme handling
    initializeTheme();
}

/**
 * Setup CSRF token for AJAX requests
 */
function setupCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    if (token) {
        window.PentestApp.csrfToken = token.getAttribute('content');
        
        // Set default AJAX headers
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", window.PentestApp.csrfToken);
                }
            }
        });
    }
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Check for browser notification permission
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
    
    // Setup toast container if not exists
    if (!document.getElementById('toastContainer')) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

/**
 * Setup periodic data refresh
 */
function setupPeriodicRefresh() {
    // Refresh system stats every 30 seconds
    setInterval(() => {
        if (typeof updateSystemStats === 'function') {
            updateSystemStats();
        }
    }, window.PentestApp.config.refreshInterval);
    
    // Refresh active scans every 10 seconds
    setInterval(() => {
        if (typeof updateActiveScans === 'function') {
            updateActiveScans();
        }
    }, 10000);
}

/**
 * Initialize theme handling
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('pentestTheme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        // Auto-detect system theme preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light');
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('pentestTheme')) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });
}

/**
 * Apply theme to the application
 */
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('pentestTheme', theme);
}

/**
 * Setup global event listeners
 */
function setupGlobalEventListeners() {
    // Handle form submissions with loading states
    document.addEventListener('submit', function(e) {
        if (e.target.classList.contains('ajax-form')) {
            e.preventDefault();
            handleAjaxForm(e.target);
        }
    });
    
    // Handle clicks on elements with data-action attributes
    document.addEventListener('click', function(e) {
        if (e.target.hasAttribute('data-action')) {
            e.preventDefault();
            const action = e.target.getAttribute('data-action');
            handleDataAction(action, e.target);
        }
    });
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        handleKeyboardShortcuts(e);
    });
    
    // Handle window resize for responsive charts
    window.addEventListener('resize', function() {
        if (window.PentestApp.charts) {
            Object.values(window.PentestApp.charts).forEach(chart => {
                if (chart && chart.resize) {
                    chart.resize();
                }
            });
        }
    });
    
    // Handle visibility change to pause/resume updates
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            console.log('Page hidden - pausing updates');
        } else {
            console.log('Page visible - resuming updates');
            if (typeof refreshAllData === 'function') {
                refreshAllData();
            }
        }
    });
}

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(function(popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Load initial application data
 */
function loadInitialData() {
    // Load user information
    fetchCurrentUser();
    
    // Load system statistics
    updateSystemStats();
    
    // Load active scans
    updateActiveScans();
}

/**
 * Handle AJAX form submissions
 */
function handleAjaxForm(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message || 'Operation completed successfully', 'success');
            
            // Handle redirect if specified
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            }
            
            // Trigger custom event
            form.dispatchEvent(new CustomEvent('ajaxSuccess', { detail: data }));
        } else {
            showToast(data.message || 'Operation failed', 'error');
            form.dispatchEvent(new CustomEvent('ajaxError', { detail: data }));
        }
    })
    .catch(error => {
        console.error('AJAX form error:', error);
        showToast('An error occurred. Please try again.', 'error');
        form.dispatchEvent(new CustomEvent('ajaxError', { detail: error }));
    })
    .finally(() => {
        // Restore button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    });
}

/**
 * Handle data-action clicks
 */
function handleDataAction(action, element) {
    switch (action) {
        case 'refresh-page':
            location.reload();
            break;
        case 'toggle-theme':
            toggleTheme();
            break;
        case 'show-shortcuts':
            showKeyboardShortcuts();
            break;
        case 'clear-notifications':
            clearAllNotifications();
            break;
        default:
            console.log('Unknown action:', action);
    }
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + K - Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], #globalSearch');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Ctrl/Cmd + Shift + N - New scan
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'N') {
        e.preventDefault();
        const newScanBtn = document.querySelector('[data-bs-target="#newScanModal"]');
        if (newScanBtn) {
            newScanBtn.click();
        }
    }
    
    // Escape - Close modals
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal.show');
        if (activeModal) {
            bootstrap.Modal.getInstance(activeModal).hide();
        }
    }
    
    // ? - Show keyboard shortcuts
    if (e.key === '?' && !e.target.matches('input, textarea')) {
        e.preventDefault();
        showKeyboardShortcuts();
    }
}

/**
 * Toggle application theme
 */
function toggleTheme() {
    const currentTheme = localStorage.getItem('pentestTheme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
    showToast(`Switched to ${newTheme} theme`, 'info');
}

/**
 * Show keyboard shortcuts modal
 */
function showKeyboardShortcuts() {
    const shortcuts = [
        { key: 'Ctrl/Cmd + K', action: 'Focus search' },
        { key: 'Ctrl/Cmd + Shift + N', action: 'New scan' },
        { key: 'Escape', action: 'Close modals' },
        { key: '?', action: 'Show shortcuts' },
        { key: 'Ctrl/Cmd + R', action: 'Refresh page' }
    ];
    
    const modalHtml = `
        <div class="modal fade" id="shortcutsModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-keyboard me-2"></i>Keyboard Shortcuts
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="shortcuts-list">
                            ${shortcuts.map(shortcut => `
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span class="shortcut-action">${shortcut.action}</span>
                                    <kbd class="shortcut-key">${shortcut.key}</kbd>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('shortcutsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to DOM and show
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('shortcutsModal'));
    modal.show();
    
    // Remove modal when hidden
    document.getElementById('shortcutsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

/**
 * Fetch current user information
 */
function fetchCurrentUser() {
    fetch('/auth/check-session')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                window.PentestApp.state.currentUser = data;
                updateUserInterface(data);
            }
        })
        .catch(error => {
            console.error('Failed to fetch user info:', error);
        });
}

/**
 * Update system statistics
 */
function updateSystemStats() {
    fetch('/api/system/stats')
        .then(response => response.json())
        .then(data => {
            window.PentestApp.state.systemStats = data;
            
            // Update UI elements
            updateSystemMetrics(data);
            updateStatsBadges(data);
            
            // Trigger custom event
            document.dispatchEvent(new CustomEvent('systemStatsUpdated', { detail: data }));
        })
        .catch(error => {
            console.error('Failed to fetch system stats:', error);
        });
}

/**
 * Update active scans
 */
function updateActiveScans() {
    fetch('/api/scans/active')
        .then(response => response.json())
        .then(data => {
            window.PentestApp.state.activeScans = data.active_scans || [];
            
            // Update UI elements
            updateActiveScansBadge(data.count || 0);
            updateActiveScansList(data.active_scans || []);
            
            // Trigger custom event
            document.dispatchEvent(new CustomEvent('activeScansUpdated', { detail: data }));
        })
        .catch(error => {
            console.error('Failed to fetch active scans:', error);
        });
}

/**
 * Update system metrics in UI
 */
function updateSystemMetrics(stats) {
    // Update CPU usage
    const cpuUsage = document.getElementById('cpuUsage');
    const cpuProgressBar = document.getElementById('cpuProgressBar');
    if (cpuUsage && stats.cpu_percent !== undefined) {
        cpuUsage.textContent = `${stats.cpu_percent}%`;
        if (cpuProgressBar) {
            cpuProgressBar.style.width = `${stats.cpu_percent}%`;
            cpuProgressBar.className = `progress-bar ${getProgressBarClass(stats.cpu_percent)}`;
        }
    }
    
    // Update memory usage
    const memoryUsage = document.getElementById('memoryUsage');
    const memoryProgressBar = document.getElementById('memoryProgressBar');
    if (memoryUsage && stats.memory_percent !== undefined) {
        memoryUsage.textContent = `${stats.memory_percent}%`;
        if (memoryProgressBar) {
            memoryProgressBar.style.width = `${stats.memory_percent}%`;
            memoryProgressBar.className = `progress-bar ${getProgressBarClass(stats.memory_percent)}`;
        }
    }
    
    // Update disk usage
    const diskUsage = document.getElementById('diskUsage');
    const diskProgressBar = document.getElementById('diskProgressBar');
    if (diskUsage && stats.disk_usage !== undefined) {
        diskUsage.textContent = `${stats.disk_usage}%`;
        if (diskProgressBar) {
            diskProgressBar.style.width = `${stats.disk_usage}%`;
            diskProgressBar.className = `progress-bar ${getProgressBarClass(stats.disk_usage)}`;
        }
    }
    
    // Update active users
    const activeUsers = document.getElementById('activeUsers');
    if (activeUsers && stats.connected_users !== undefined) {
        activeUsers.textContent = stats.connected_users;
    }
}

/**
 * Get progress bar class based on percentage
 */
function getProgressBarClass(percentage) {
    if (percentage >= 90) return 'bg-danger';
    if (percentage >= 75) return 'bg-warning';
    if (percentage >= 50) return 'bg-info';
    return 'bg-success';
}

/**
 * Update statistics badges
 */
function updateStatsBadges(stats) {
    const elements = {
        'activeScansCount': stats.active_scans,
        'completedScansCount': stats.scans_completed,
        'vulnerabilitiesCount': stats.vulnerabilities_found
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            animateNumberChange(element, value);
        }
    });
}

/**
 * Update active scans badge
 */
function updateActiveScansBadge(count) {
    const badge = document.getElementById('activeScansBadge');
    if (badge) {
        badge.textContent = count;
        badge.className = count > 0 ? 'badge bg-primary' : 'badge bg-secondary';
    }
}

/**
 * Update active scans list
 */
function updateActiveScansList(scans) {
    const tableBody = document.getElementById('activeScansList');
    if (!tableBody) return;
    
    if (scans.length === 0) {
        tableBody.innerHTML = `
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
    
    tableBody.innerHTML = scans.map(scan => `
        <tr>
            <td>${escapeHtml(scan.target)}</td>
            <td>
                <span class="badge badge-status bg-info">${escapeHtml(scan.scan_type)}</span>
            </td>
            <td>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar ${getProgressBarClass(scan.progress || 0)}" 
                         role="progressbar" 
                         style="width: ${scan.progress || 0}%">
                        ${scan.progress || 0}%
                    </div>
                </div>
            </td>
            <td>
                <span class="badge ${getStatusBadgeClass(scan.status)}">${escapeHtml(scan.status)}</span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-outline-primary" 
                            onclick="viewScanDetails('${scan.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" 
                            onclick="stopScan('${scan.id}')" title="Stop Scan">
                        <i class="fas fa-stop"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Get status badge class
 */
function getStatusBadgeClass(status) {
    const statusClasses = {
        'starting': 'bg-info',
        'running': 'bg-primary',
        'completed': 'bg-success',
        'failed': 'bg-danger',
        'stopped': 'bg-warning'
    };
    return `badge ${statusClasses[status] || 'bg-secondary'}`;
}

/**
 * Animate number changes
 */
function animateNumberChange(element, newValue) {
    const currentValue = parseInt(element.textContent) || 0;
    if (currentValue === newValue) return;
    
    const increment = newValue > currentValue ? 1 : -1;
    const duration = Math.min(Math.abs(newValue - currentValue) * 50, 1000);
    const steps = Math.abs(newValue - currentValue);
    const stepDuration = duration / steps;
    
    let current = currentValue;
    const timer = setInterval(() => {
        current += increment;
        element.textContent = current;
        
        if (current === newValue) {
            clearInterval(timer);
        }
    }, stepDuration);
}

/**
 * Update user interface elements
 */
function updateUserInterface(userData) {
    // Update username displays
    document.querySelectorAll('.user-name').forEach(element => {
        element.textContent = userData.username || 'User';
    });
    
    // Update role badges
    document.querySelectorAll('.user-role').forEach(element => {
        element.textContent = userData.role || 'user';
        element.className = `badge ${userData.role === 'admin' ? 'bg-danger' : 'bg-info'} user-role`;
    });
    
    // Show demo mode indicator
    if (userData.demo_mode) {
        showDemoModeIndicator();
    }
}

/**
 * Show demo mode indicator
 */
function showDemoModeIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'alert alert-info alert-dismissible fade show position-fixed';
    indicator.style.cssText = 'top: 80px; right: 20px; z-index: 9998; max-width: 300px;';
    indicator.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        <strong>Demo Mode:</strong> You have limited access to features.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(indicator);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.remove();
        }
    }, 10000);
}

/**
 * Clear all notifications
 */
function clearAllNotifications() {
    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        toastContainer.innerHTML = '';
    }
    showToast('All notifications cleared', 'info');
}

/**
 * Refresh all data
 */
function refreshAllData() {
    updateSystemStats();
    updateActiveScans();
    
    // Trigger page-specific refresh if available
    if (typeof refreshPageData === 'function') {
        refreshPageData();
    }
}

/**
 * Utility function to escape HTML
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Utility function to format dates
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Utility function to format file sizes
 */
function formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Show confirmation dialog
 */
function showConfirmation(message, callback, title = 'Confirm Action') {
    const modal = document.getElementById('confirmModal');
    if (modal) {
        document.querySelector('#confirmModal .modal-title').textContent = title;
        document.getElementById('confirmMessage').textContent = message;
        
        const confirmBtn = document.getElementById('confirmAction');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        newConfirmBtn.addEventListener('click', function() {
            callback();
            bootstrap.Modal.getInstance(modal).hide();
        });
        
        new bootstrap.Modal(modal).show();
    } else {
        if (confirm(message)) {
            callback();
        }
    }
}

// Expose utility functions globally
window.showToast = showToast;
window.showConfirmation = showConfirmation;
window.formatDate = formatDate;
window.formatFileSize = formatFileSize;
window.escapeHtml = escapeHtml;
window.refreshAllData = refreshAllData;